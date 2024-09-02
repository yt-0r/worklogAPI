import logging
import traceback
from datetime import datetime
from typing import List, Dict, Union, AnyStr, Any
import requests

from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html

from sqlalchemy.exc import ProgrammingError

from bot.notification import Notification
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

from config import Settings

settings: Settings

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css")


applications.post_swagger_ui_html = swagger_monkey_patch

app = FastAPI(
    title='its-api'
)


@app.post('/worklog')
def worklog(url: str, data: JSONStructure = None):
    server = url.split('.')[0].split('//')[1]
    # Подгружаем конфиг
    global settings
    settings = Settings(_env_file=f'{server}.env')

    # Настраиваем лог
    requests.post(f'{settings.SERVICE_REST}/service/log/set?filename={server}_worklog.log')
    # Пишем в лог
    requests.post(
        f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=START ON {url.split("//")[1].upper()}')

    # Пишем в файл сырой JSON
    requests.post(f'{settings.SERVICE_REST}/service/file?url={url}&filename=raw.json', json=data)

    # Нормализуем
    json_normalize = requests.post(f'{settings.SERVICE_REST}/logic/normalize?url={url}', json=data).json()
    requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=Normalize JSON - OK!')
    # пишем в файл
    requests.post(f'{settings.SERVICE_REST}/service/file?url={url}&filename=normalized.json', json=json_normalize)
    # пишем в raw
    requests.post(f'{settings.SERVICE_REST}/database/raw?url={url}', json=json_normalize).json()

    # Калькулируем
    json_calc = requests.post(f'{settings.SERVICE_REST}/logic/calculate?url={url}', json=json_normalize).json()
    requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=Calc JSON - OK!')
    # пишем в файл
    requests.post(f'{settings.SERVICE_REST}/service/file?url={url}&filename=calculated.json', json=json_calc)
    # пишем в clock
    requests.post(f'{settings.SERVICE_REST}/database/clock?url={url}', json=json_calc)

    # Делаем словарь из данных
    months = pd.DataFrame(json_calc).drop_duplicates(['period_month', 'period_year'])['period_month'].to_list()
    years = pd.DataFrame(json_calc).drop_duplicates(['period_month', 'period_year'])['period_year'].to_list()
    months_years = dict(zip(months, years))

    # Создаём excel
    res = requests.post(f'{settings.SERVICE_REST}/create_excel?url={url}', json=months_years).json()

    if res['status_code'] != 200:
        return {'status_code': 500, 'text': 'Internal error !'}
    else:
        return {'status_code': 200, 'text': 'Create excel !'}


#
@app.post('/service/log/set')
def service_log_set(filename):
    Logging.log_set(filename)
    return {'status_code': 200, 'text': 'Log set OK!'}


@app.post('/service/telegram')
def telegram(server: str, msg: Union[str, None] = 'Ошибка!'):
    Notification.send_to_telegram(server, msg)


@app.post('/logic/normalize', response_model=List[Workers])
def normalize(url: str, data: JSONStructure = None):
    server = url.split('.')[0].split('//')[1]
    try:
        Normalize.data = data
        json_normalized = Normalize.js_to_norm(server)
        json_valid = list(map(lambda i: Workers.model_validate(i).__dict__, json_normalized))
        return json_valid
    except Exception:
        # делаем запрос на конечные точки
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={traceback.format_exc()}')
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        # Отправляем в телегу
        requests.post(f'{settings.SERVICE_REST}/service/telegram?server={server}&msg={traceback.format_exc()}')
        return {'status_code': 500, 'text': 'Normalize Fail!'}


@app.post('/create_excel')
def excel(url: str, year: Union[str, None] = None, staff: Union[str, None] = None, dep: Union[str, None] = None,
          months: Union[Dict[str, int], None] = None):
    server = url.split('.')[0].split('//')[1]
    settings = Settings(_env_file=f'{server}.env')
    try:
        Excel.create_excel(server=server, url=url, months_years=months, years=year, dep=dep, worker=staff)
        return {'status_code': 200, 'text': 'Excel OK!'}
    except Exception as er:
        msg = traceback.format_exc() if len(traceback.format_exc()) < 1024 else er
        # делаем запрос на конечные точки
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={traceback.format_exc()}')
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        # Отправляем в телегу
        requests.post(f'{settings.SERVICE_REST}/service/telegram?server={server}&msg={msg}')
        return {'status_code': 500, 'text': 'Excel Fail!'}


@app.post('/logic/calculate', response_model=List[Workers])
def calc(url: str, data: List[Workers]):
    server = url.split('.')[0].split('//')[1]
    try:
        json_to_calc = [i.__dict__ for i in data]
        json_calculated = Calculator.calc_workers(json_to_calc)
        return json_calculated
    except Exception:
        # делаем запрос на конечные точки
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={traceback.format_exc()}')
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        # Отправляем в телегу
        requests.post(f'{settings.SERVICE_REST}/service/telegram?server={server}&msg={traceback.format_exc()}')
        return {'status_code': 500, 'text': 'Calc Fail!'}


@app.post('/service/log')
def service_log_add(level: int, message: str):
    Logging.log_add(level, message)
    return 'OK!'


@app.post('/service/file')
def service_file(url: str, filename: Union[str, None] = f'{datetime.now()}.json', data: JSONStructure = None):
    server = url.split('.')[0].split('//')[1]
    settings = Settings(_env_file=f'{server}.env')

    JsonFile.record(data, filename)
    requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=Record JSON to {filename}')
    return 'OK!'


@app.post('/database/{name}')
def database(name: str, url: str, data: List[Workers]):
    server = url.split('.')[0].split('//')[1]
    try:
        data_from_json = [i.__dict__ for i in data]
        if name == 'raw':
            model = RawJS

        if name == 'clock':
            model = ClockJS

        try:
            data_from_database = SyncORM.select_data(data_from_json, model, server, url)
        except ProgrammingError as er:
            requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message={str(er)}')
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
        return {'status_code': 200, 'text': 'Database OK!'}

    except Exception:
        # делаем запрос на конечные точки
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={traceback.format_exc()}')
        requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')
        # Отправляем в телегу
        requests.post(f'{settings.SERVICE_REST}/service/telegram?server={server}&msg={traceback.format_exc()}')
        return {'status_code': 500, 'text': 'Database Fail!'}
