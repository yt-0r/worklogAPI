from doccorp.date_time import DateTime
from doccorp.reference import Reference
from doccorp.contracts import Contracts
from doccorp.other import Components
from doccorp.FIO_declension import PytrovichFIO
from doccorp.position_declension import PymorphyPos
from doccorp.sign import Sign
from doccorp.system import System
from doccorp.tables import Tables
from doccorp.true_date import TrueDate


class DataKeywords:
    issuekey: str
    issuetype: str
    project: str

    def __init__(self, data):
        self.true_json = []

        try:
            data = data[0]
        except KeyError:
            data = data

        DataKeywords.issuekey = data['issuekey']

        try:
            DataKeywords.project = data['project']
            DataKeywords.issuetype = data['issuetype']
        except KeyError:
            pass

        # получаем словарь с индексами
        methods = list(data['fields'].keys())

        if 'Personal' in methods:
            for record in data['fields']['Personal']:
                PytrovichFIO(record)

            self.true_json.append(
                {'method': 'Personal', 'description': 'Это переменные имён', 'var': PytrovichFIO.true_list})

            PytrovichFIO.true_list = []

        if 'Positions' in methods:
            for record in data['fields']['Positions']:
                PymorphyPos(record)
            self.true_json.append(
                {'method': 'Positions', 'description': 'Это переменные должностей', 'var': PymorphyPos.true_list})

            PymorphyPos.true_list = []

        if 'Dates' in methods:
            for record in data['fields']['Dates']:
                TrueDate(record)
            self.true_json.append(
                {'method': 'Dates', 'description': 'Это переменные дат', 'var': TrueDate.true_list})

            TrueDate.true_list = []

        if 'DateTime' in methods:
            for record in data['fields']['DateTime']:
                DateTime(record)
            self.true_json.append(
                {'method': 'DateTime', 'description': 'Это переменные даты/времени', 'var': DateTime.true_list}
            )
            DateTime.true_list = []

        if 'Components' in methods:
            for record in data['fields']['Components']:
                Components(record)
            self.true_json.append(
                {'method': 'Components', 'description': 'Это переменные компонентов документа',
                 'var': Components.true_list}
            )

            Components.true_list = []

        if 'Contracts' in methods:
            for record in data['fields']['Contracts']:
                Contracts(record)
            self.true_json.append(
                {'method': 'Contracts', 'description': 'Это переменные контрактов', 'var': Contracts.true_list}
            )

            Contracts.true_list = []

        if 'Sign' in methods:
            for record in data['fields']['Sign']:
                Sign(record)
            self.true_json.append(
                {'method': 'Sign', 'description': 'Это переменные подписей', 'var': Sign.true_list}
            )
            Sign.true_list = []

        if 'Tables' in methods:
            for record in data['fields']['Tables']:
                Tables(record)
            self.true_json.append(
                {'method': 'Tables', 'description': 'Это таблицы', 'var': Tables.true_list}
            )
            Tables.true_list = []

        # if 'systemfield' in methods:
        #     for record in data['fields']['systemfield']:
        #         System(record)
        #     self.true_json.append(
        #         {'method': 'systemfield', 'description': 'Это системные переменные с заявки', 'var': System.true_list}
        #     )
        #     System.true_list = []
