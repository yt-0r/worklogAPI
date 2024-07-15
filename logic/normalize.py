import json
import logging
import sys
from typing import List, Dict
import traceback

import pandas as pd
import numpy as np
import requests

from config import settings


class Normalize:
    """
    data: dict, list_path: list, list_meta: list, cols_to_norm: list, dict_fillna: dict, merge_method: str

    1)data - содержит JSON

    2)list_path - содержит пути к спискам записей в JSON. ТИП - список строк / список списков строк.

    3)list_meta - содержит пути к определенным полям в JSON, которые будут использоваться в DataFrame.
    список строк / список списков строк
    если такого нет, то передаем пустой список list_meta=[]

    4)cols_to_norm - содержит пути к спискам записей в JSON, которые были в списках записей (вложены).
    строка / список строк
    если вложенностей нет, то пишем cols_to_norm=[]

    5)dict_fillna - содержит словарь, ключи которого, содержат столбцы DataFrame, в которых надо поменять
    отсутсвующие данные(Nan) на те, которые указаны в словаре.
    если замена не требуется, то передаем пустой словарь dict_fillna={}

    6)merge_method - содержит один из методов слияния: "left","right","outer","inner","cross"
    left - использовать только ключи из левого фрейма, аналогично левому соединению SQL; сохранить порядок ключей.
    right - использовать только ключи из правого фрейма, аналогично правому соединению SQL; сохранить порядок ключей
    outer - использовать объединение ключей из обоих фреймов, аналогично полному соединению SQL;
    inner - использовать пересечение ключей из обоих фреймов, аналогично внутреннему соединению SQL;
    cross - создает декартово произведение из обоих фреймов, сохраняет порядок левых ключей.
    merge_method используется только при обработке JSON, в которых есть множество записей.
    если множества записей нет, то передаем пустую строку merge_method=''
    При выборе метода мержа, рекомендуется потыкать разные методы и посмотреть, какой подойдёт

    ВНИМАНИЕ!!!
    Информация ниже требует проверки.
    Если в списках записей нет одинаковых ключей, то cross. Если в списках записей есть одинковые ключи, то outer

    после инициализации объекта класса, необходимо передать JSON в поле data
    """

    data = []

    list_path = ["days"]

    list_meta = [["job", "name"], ["job", "department"], ["job", "position"], ['period', 'month'], ["period", "year"]]

    cols_to_norm = ["kontrakt"]

    dict_fillna = {'kontrakt_issuecount': 0, 'kontrakt_filter': '0', 'kontrakt_timetracking': 0, 'kontrakt_type': 0}

    merge_method = 'cross'

    @classmethod
    def js_to_norm(cls):
        try:
            if len(cls.list_path) == 0:
                df_json = pd.json_normalize(cls.data, meta=cls.list_meta, sep='_', errors="ignore")
                df_json = df_json.apply(lambda x: x.explode()).reset_index(drop=True)
            else:
                df_json = pd.json_normalize(cls.data, record_path=cls.list_path[0], meta=cls.list_meta, sep='_',
                                            errors="ignore")
                df_json = df_json.apply(lambda x: x.explode()).reset_index(drop=True)
                for i in range(1, len(cls.list_path)):
                    df_temp = pd.json_normalize(cls.data, record_path=cls.list_path[i], sep=' ', errors="ignore")
                    df_temp = df_temp.apply(lambda x: x.explode()).reset_index(drop=True)
                    df_json = df_json.merge(df_temp, how=cls.merge_method)
            if len(cls.cols_to_norm) != 0:
                normalized = list()
                for col in cls.cols_to_norm:
                    d = pd.json_normalize(df_json[col], sep='_')
                    d.columns = [f'{col}_{v}' for v in d.columns]
                    normalized.append(d.copy())
                df_json = pd.concat([df_json] + normalized, axis=1).drop(columns=cls.cols_to_norm)
            for i in cls.dict_fillna:
                df_json = df_json.fillna({i: cls.dict_fillna[i]})

            if 'kontrakt_timetracking' in df_json:
                df_json['kontrakt_timetracking'] = (df_json['kontrakt_timetracking'].
                                                    apply(lambda x: [{'0': [0, 0]}] if x == 0 else x))

            df_json = df_json.explode('kontrakt_timetracking', ignore_index=True)

            requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=Normalize JSON - OK!')

            return list(df_json.to_dict('index').values())

        except KeyError as key:
            # делаем запрос на конечную точку
            requests.get(
                f'{settings.SERVICE_REST}/service/log?level={logging.ERROR}&message={str(traceback.format_exc())}')

            requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=STOP SCRYPT')

            sys.exit()

    @staticmethod
    def to_df(df_json):
        return pd.DataFrame(df_json)
