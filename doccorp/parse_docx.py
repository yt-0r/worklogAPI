import json
import re

import docx2txt


class Docx:
    true_json = {}

    @classmethod
    def valid_docx(cls, filename, directory):

        cls.true_json['Issue'] = directory

        vars_docx = cls.__getText(filename)
        vars_json = cls.__getVar(directory)

        error_list = []

        # сравниваем переменные из шаблона и из json, если в шаблоне что-то неправильно, добавляем неправильную переменную из шаблона в список
        for var in vars_docx:
            if var not in vars_json:
                error_list.append(var)

        # если список не пустой, то вернем json об ошибке
        if error_list:
            cls.true_json['Validation'] = 'failed'
            cls.true_json['Var'] = {var: "not found" for var in error_list}

        else:
            # отсекаем сюда переменные из jira
            jira_vars = list(set([var.split('_') for var in vars_docx]))

        return cls.true_json

    @staticmethod
    def __getVar(directory: str):
        with open(f'{directory}.json', 'r', encoding='utf-8') as file:
            json_vars = json.load(file)
        list_vars = []
        for record in json_vars:
            list_vars.extend([var for var in record['var']])
        return list_vars

    @staticmethod
    def __getText(filename: str):
        text = docx2txt.process(filename)
        matches = re.findall(r"{{(.*)}}", text)

        return matches
