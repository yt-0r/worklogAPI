import logging
import sys
import traceback
from typing import List, Dict, Union
import requests
import json

from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import ValidationError
from pydantic_settings import BaseSettings
from requests.auth import HTTPBasicAuth
from sqlalchemy.exc import ProgrammingError

from database.orm import SyncORM
from logic.json_manager import JsonManager
from logic.normalize import Normalize
from models.json_model import Workers
from service.to_log import Logging
from service.to_file import JsonFile

from models.database_model import RawJS, ClockJS
from excel.excel import Excel
from logic.calculate import Calculator
import pandas as pd


# from config import settings


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css")


applications.get_swagger_ui_html = swagger_monkey_patch

app = FastAPI(
    title='test'
)

from config import Settings

settings: Settings


@app.get('/worklog')
def worklog(date: str, server: str):
    global settings
    settings = Settings(_env_file=f'{server}.env')

    requests.get(f'{settings.SERVICE_REST}/service/log/set')

    json_normalized = json.loads(requests.get(f'{settings.SERVICE_REST}/logic/normalize?date={date}&server={server}').text)
    json_calculated = json.loads(requests.post(f'{settings.SERVICE_REST}/logic/calculate?server={server}', json=json_normalized).text)

    months = pd.DataFrame(json_calculated).drop_duplicates(['period_month', 'period_year'])['period_month'].to_list()
    years = pd.DataFrame(json_calculated).drop_duplicates(['period_month', 'period_year'])['period_year'].to_list()
    months_years = dict(zip(months, years))

    requests.post(f'{settings.SERVICE_REST}/create_exel?server={server}', json=months_years)
    return 'create excel!'


@app.get('/service/log/set')
def service_log_set():
    Logging.log_set()
    return 'OK!'


@app.get('/logic/normalize', response_model=List[Workers])
def normalize(date: str, server: str):
    try:
        rest = settings.JIRA_REST + date
        response = requests.get(rest, auth=HTTPBasicAuth(settings.ZABBIX_USER, settings.ZABBIX_PASSWORD))
        json_jira = json.loads(response.text)

        Normalize.data = json_jira
        json_normalized = Normalize.js_to_norm(server)

        json_valid = list(map(lambda i: Workers.model_validate(i).__dict__, json_normalized))

        # пишем в файл
        requests.post(f'{settings.SERVICE_REST}/service/file?name=raw.json', json=json_valid)

        # пишем в raw
        requests.post(f'{settings.SERVICE_REST}/database/raw?server={server}', json=json_valid)

        return json_valid

    except ValidationError as er:
        # делаем запрос на конечные точки
        requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={str(er)}')
        requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        sys.exit()

    except OSError as er:
        # делаем запрос на конечные точки
        requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={str(er)}')
        requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        sys.exit()


@app.post('/create_exel')
def excel(server: str, months: Dict[str, int]):
    Excel.create_excel(months, server)
    return 'Ok!'


@app.post('/logic/calculate', response_model=List[Workers])
def calc(server: str, data: List[Workers]):
    json_to_calc = [i.__dict__ for i in data]
    json_calculated = Calculator.calc_workers(json_to_calc)
    requests.post(f'{settings.SERVICE_REST}/service/file?name=calculated.json', json=json_calculated)
    requests.post(f'{settings.SERVICE_REST}/database/clock?server={server}', json=json_calculated)
    return json_calculated


@app.get('/service/log')
def service_log_add(level: int, message: str):
    Logging.log_add(level, message)


@app.post('/service/file')
def service_file(data: List[Workers], name: Union[str, None] = '.json'):
    json_to_record = [i.__dict__ for i in data]
    JsonFile.record(json_to_record, name)
    requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&'
                 f'message=Record JSON to {name}')
    return 'good!'


@app.post('/database/{name}')
def database(name: str, server: str, data: List[Workers]):
    try:
        data_from_json = [i.__dict__ for i in data]

        if name == 'raw':
            model = RawJS

        if name == 'clock':
            model = ClockJS

        try:
            data_from_database = SyncORM.select_data(data_from_json, model)
        except ProgrammingError:
            requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&'
                         f'ProgrammingError')
            data_from_database = []

        # соединяем данные с json и базы
        data_json_database = JsonManager.merge(data_from_json, data_from_database, server)

        # группируем
        group_data_json_database = JsonManager.group(data_json_database)

        # создаем таблицы
        SyncORM.create_table()

        # удаляем данные
        SyncORM.delete_data(data_from_json, model)

        # пишем данные
        SyncORM.insert_data(group_data_json_database, model)

        # пишем лог
        requests.get(
            f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=Update data in {name} database - OK!')
        return 'OK!'

    except Exception as er:
        requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={traceback.format_exc()}')
        sys.exit()
