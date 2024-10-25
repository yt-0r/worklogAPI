import json
import re

import docx2txt


class Docx:
    true_json = {}

    @classmethod
    def valid_docx(cls, filename, directory):
        cls.true_json: dict
        cls.true_json['issuekey'] = directory

        vars_docx = cls.__getText(filename)
        vars_json = cls.__getJson(directory)

        error_list = []

        # сравниваем переменные из шаблона и из json, если в шаблоне что-то неправильно, добавляем неправильную переменную из шаблона в список
        for var in vars_docx:
            if var not in vars_json:
                error_list.append(var)

        # если список не пустой, то вернем json об ошибке
        if error_list:
            cls.true_json['validation'] = 'failed'
            cls.true_json['fields'] = {var: 'не найдено' for var in error_list}

        else:
            cls.true_json['validation'] = 'success'
            cls.true_json['fields'] = {}

            with open(f'jsons/{directory}.json', 'r', encoding='utf-8') as file:
                json_blocks_vars = json.load(file)

            # отсекаем сюда переменные из шаблона
            vars_docx = list(set([f'customfield_{var.split("_")[-1]}' for var in vars_docx]))

            # возвращаем Женьку красивую структуру

            yet_list = []
            result_list = []
            for block in json_blocks_vars:
                temp_list = []
                for var in block['var']:
                    if var['id'] in vars_docx and var['id'] not in yet_list:
                        yet_list.append(var['id'])
                        var.pop('var')
                        var.pop('value')
                        temp_list.append(var)

                cls.true_json['fields'][block['method']] = temp_list

        return cls.true_json

    @staticmethod
    def __getJson(directory: str):
        with open(f'jsons/{directory}.json', 'r', encoding='utf-8') as file:
            json_vars = json.load(file)
        list_vars = []
        for record in json_vars:
            list_vars.extend([var['var'].split(' ')[-1] for var in record['var']])

        return list_vars

    @staticmethod
    def __getText(filename: str):
        text = docx2txt.process(filename)

        matches = re.findall(r"\{\{(.*?)\}\}", text)
        matches = [s.split(' ')[-1] for s in matches]

        return matches
