import base64
import json
import os
import traceback
from datetime import datetime

from typing import List, Dict, Union, AnyStr, Any, Annotated
import requests

from fastapi import FastAPI, applications, File, UploadFile
from fastapi.openapi.docs import get_swagger_ui_html

from sqlalchemy.exc import ProgrammingError

from bot.notification import Notification
from database.orm import SyncORM
from doccorp.create_doc import DoccorpTemplate
from doccorp.parse_docx import Docx
from logic.json_manager import JsonManager
from logic.normalize import Normalize
from models.json_model import Workers
from service.to_file import JsonFile

from models.database_model import RawJS, ClockJS
from my_excel.excels import Excel
from logic.calculate import Calculator
import pandas as pd
import random
from docxtpl import DocxTemplate
from config import Settings
from doccorp.data_keywords2 import DataKeywords

from service.to_log import Logging

settings: Settings

JSONObject = Dict[AnyStr, Any]
JSONArray = List[Any]
JSONStructure = Union[JSONArray, JSONObject]

import logging


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css")


applications.post_swagger_ui_html = swagger_monkey_patch

app = FastAPI(
    title='its-api'
)

REST = 'http://127.0.0.1:8000'


# админ
# 194020

# оператор2
# 194036

@app.post('/redirect')
def redirect(data: JSONStructure = None):
    try:
        requests.post(f'{REST}/service/log/set?cfg=redirect')
        requests.post(f'{REST}/service/file?url=http://jira.its-sib.ru&filename=redirect.json', json=data)

        employee = data['staff']
        phone = str(data['telephone'])

        if data['department'] == 'Отдел 1-ой линии технической поддержки':
            user_id = 194036

            token = 'y24mdilhj78xyv35hzaahrcgo43rlek5hjjpbulv'
            data_novofon = {
                "jsonrpc": "2.0",
                "id": random.randint(1, 1000),
                "method": "update.employees",
                "params": {
                    "access_token": token,
                    "id": user_id,
                    "phone_numbers": [
                        {
                            "phone_number": phone,
                            "channels_count": 2,
                            "dial_time": 60,
                            "status": "active"
                        }
                    ]
                }
            }

            if user_id == 194036:
                call = requests.post(url='https://dataapi-jsonrpc.novofon.ru/v2.0', json=data_novofon).json()
                if 'error' in call.keys():
                    msg = call['error']['message']
                    requests.post(f'{REST}/service/log?level={logging.ERROR}&message={msg}')
                    return {'status_code': 500, 'text': msg}
                else:
                    msg = f'success redirect to {employee} ({data["telephone"]})'
                    requests.post(f'{REST}/service/log?level={logging.INFO}&message={msg}')
                    return {'status_code': 200, 'text': msg}
        else:
            msg = f'NO REDIRECT TO {employee} ({data["telephone"]})'
            requests.post(f'{REST}/service/log?level={logging.INFO}&message={msg}')
            return {'status_code': 200, 'text': msg}

    except Exception:
        requests.post(f'{REST}/service/telegram?server=jira&msg={traceback.format_exc()}')
        return {'status_code': 500, 'text': 'error'}


@app.post('/add_page_template')
def add_page_template(data: JSONStructure):
    requests.post(f'{REST}/service/log/set?cfg=doc')

    directory = data['issue']

    # Декодируем строку Base64

    requests.post(f'{REST}/service/log?level={logging.INFO}&message=START VALIDATE {directory}')

    decoded_bytes = base64.b64decode(data['template'])
    with open(f'templates/{directory}.docx', 'wb') as fd:
        fd.write(decoded_bytes)
        fd.close()

    text = Docx.valid_docx(f'templates/{directory}.docx', directory)

    if text['validation'] == 'failed':
        os.remove(f'templates/{directory}.docx')
        requests.post(f'{REST}/service/log?level={logging.INFO}&message=VALIDATE {directory} - FAILED')

    else:
        requests.post(f'{REST}/service/log?level={logging.INFO}&message=VALIDATE {directory} - SUCCESS ')
    return text


@app.post('/valid_json')
def valid_json(data: JSONStructure = None):
    requests.post(f'{REST}/service/log/set?cfg=doc')
    to_jira = DataKeywords(data)
    issue = DataKeywords.issuekey
    requests.post(f'{REST}/service/file?url=http://jira.its-sib.ru&filename={issue}.json', json=to_jira.true_json)
    return to_jira.true_json


@app.post("/create_doc")
def create_file(data: JSONStructure = None):

    to_doc = DataKeywords(data)
    issue = DataKeywords.issuekey

    with open('templates/query.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    render_dict = {}
    for method in to_doc.true_json:
        for var in method['var']:
            render_dict[var['var'].split(' ')[-1]] = var['value']

    with open('templates/render_dict.json', 'w', encoding='utf-8') as file:
        json.dump(render_dict, file, indent=2, ensure_ascii=False)

    doccorp = DoccorpTemplate(issue)
    result = doccorp.my_render(render_dict)

    return {'issuekey': issue, 'pdf': result}


@app.post('/worklog')
def worklog(url: str, data: JSONStructure = None):
    server = url.split('.')[0].split('//')[1]
    # Подгружаем конфиг
    global settings
    settings = Settings(_env_file=f'{server}.env')

    requests.post(f'{settings.SERVICE_REST}/service/log/set?cfg={server}_worklog')

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

    # Создаём my_excel
    res = requests.post(f'{settings.SERVICE_REST}/create_excel?url={url}', json=months_years).json()

    if res['status_code'] != 200:
        return {'status_code': 500, 'text': 'Internal error !'}
    else:
        return {'status_code': 200, 'text': 'Create my_excel !'}


@app.post('/service/log/set')
def service_log_set(cfg):
    Logging(cfg)
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
