import logging
import sys
import traceback
from typing import List, Dict, Union, AnyStr, Any
import requests
import json

from fastapi import FastAPI, applications, Body
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import ValidationError
from requests.auth import HTTPBasicAuth
from sqlalchemy.exc import ProgrammingError

from database.orm import SyncORM
from logic.json_manager import JsonManager
from logic.normalize import Normalize
from models.json_model import Workers, Raw
from service.to_log import Logging
from service.to_file import JsonFile

from models.database_model import RawJS, ClockJS
from excel.excel import Excel
from logic.calculate import Calculator
import pandas as pd


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css")


applications.post_swagger_ui_html = swagger_monkey_patch

app = FastAPI(
    title='test'
)

from config import Settings

settings: Settings

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


@app.post('/worklog')
def worklog(url: str, data: JSONStructure = None):
    server = url.split('.')[0].split('//')[1]

    global settings
    settings = Settings(_env_file=f'{server}.env')

    requests.post(f'{settings.SERVICE_REST}/service/log/set')
    requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=START '
                  f'ON {url.split('//')[1]}')

    json_normalized = json.loads(
        requests.post(f'{settings.SERVICE_REST}/logic/normalize?url={url}', json=data).text)

    json_calculated = json.loads(
        requests.post(f'{settings.SERVICE_REST}/logic/calculate?url={url}', json=json_normalized).text)

    months = pd.DataFrame(json_calculated).drop_duplicates(['period_month', 'period_year'])['period_month'].to_list()
    years = pd.DataFrame(json_calculated).drop_duplicates(['period_month', 'period_year'])['period_year'].to_list()
    months_years = dict(zip(months, years))

    res = requests.post(f'{settings.SERVICE_REST}/create_exel?url={url}', json=months_years)

    return {'status_code': 200, 'text': 'create excel!'} if res.status_code == 200 else {'status_code': 500,
                                                                                         'text': 'internal error !!!!!'}


@app.post('/service/log/set')
def service_log_set():
    Logging.log_set()
    return {'OK!'}


@app.post('/logic/normalize', response_model=List[Workers])
def normalize(url: str, data: JSONStructure = None):
    try:
        server = url.split('.')[0].split('//')[1]

        Normalize.data = data
        json_normalized = Normalize.js_to_norm(server)

        json_valid = list(map(lambda i: Workers.model_validate(i).__dict__, json_normalized))

        # пишем в файл
        requests.post(f'{settings.SERVICE_REST}/service/file?name=raw.json', json=json_valid)

        # пишем в raw
        requests.post(f'{settings.SERVICE_REST}/database/raw?url={url}', json=json_valid)

        return json_valid

    except ValidationError as er:

        # делаем запрос на конечные точки
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={str(er)}')
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        sys.exit()

    except OSError as er:
        # делаем запрос на конечные точки
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={str(er)}')
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        sys.exit()


@app.post('/create_exel')
def excel(url: str, months: Dict[str, int]):
    server = url.split('.')[0].split('//')[1]
    Excel.create_excel(months, server, url)
    return 'OK!'


@app.post('/logic/calculate', response_model=List[Workers])
def calc(url: str, data: List[Workers]):
    json_to_calc = [i.__dict__ for i in data]
    json_calculated = Calculator.calc_workers(json_to_calc)
    requests.post(f'{settings.SERVICE_REST}/service/file?name=calculated.json', json=json_calculated)
    requests.post(f'{settings.SERVICE_REST}/database/clock?url={url}', json=json_calculated)
    return json_calculated


@app.post('/service/log')
def service_log_add(level: int, message: str):
    Logging.log_add(level, message)
    return 'OK!'


@app.post('/service/file')
def service_file(data: List[Workers], name: Union[str, None] = '.json'):
    json_to_record = [i.__dict__ for i in data]
    JsonFile.record(json_to_record, name)
    requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&'
                  f'message=Record JSON to {name}')
    return 'OK!'


@app.post('/database/{name}')
def database(name: str, url: str, data: List[Workers]):
    try:
        data_from_json = [i.__dict__ for i in data]
        server = url.split('.')[0].split('//')[1]
        if name == 'raw':
            model = RawJS

        if name == 'clock':
            model = ClockJS

        try:
            data_from_database = SyncORM.select_data(data_from_json, model, server, url)
        except ProgrammingError:
            requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&'
                          f'ProgrammingError')
            data_from_database = []

        # соединяем данные с json и базы
        data_json_database = JsonManager.merge(data_from_json, data_from_database, server)

        # группируем
        group_data_json_database = JsonManager.group(data_json_database)

        # создаем таблицы
        SyncORM.create_table(server, url)

        # удаляем данные
        SyncORM.delete_data(data_from_json, model, server, url)

        # пишем данные
        SyncORM.insert_data(group_data_json_database, model, server, url)

        # пишем лог
        requests.post(
            f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=Update data in {name} database - OK!')
        return 'OK!'

    except Exception as er:
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={traceback.format_exc()}')
        sys.exit()
