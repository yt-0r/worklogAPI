from doccorp.other import Components
from doccorp.FIO_declension import PytrovichFIO
from doccorp.position_declension import PymorphyPos
from doccorp.true_date import TrueDate


class DataKeywords:
    true_json = []
    issue: str

    def __init__(self, json):
        # получаем словарь с индексами
        methods = {json['Body'][i]['method']: i for i in range(len(json['Body']))}
        DataKeywords.issue = json['Issue']

        if 'Personal' in methods.keys():
            for key, val in json['Body'][methods['Personal']]['var'].items():
                PytrovichFIO(val, key)

            DataKeywords.true_json.append(
                {'method': 'Personal', 'description': 'Это переменные имён', 'var': PytrovichFIO.true_dict})

        if 'Dates' in methods.keys():
            for key, val in json['Body'][methods['Dates']]['var'].items():
                TrueDate(val, key)
            DataKeywords.true_json.append(
                {'method': 'Dates', 'description': 'Это переменные дат', 'var': TrueDate.true_dict})

        if 'Positions' in methods.keys():
            for key, val in json['Body'][methods['Positions']]['var'].items():
                PymorphyPos(val, key)
            DataKeywords.true_json.append(
                {'method': 'Positions', 'description': 'Это переменные должностей', 'var': PymorphyPos.true_dict})

        if 'Components' in methods.keys():
            for key, val in json['Body'][methods['Components']]['var'].items():
                Components(val, key)
            DataKeywords.true_json.append(
                {'method': 'Components', 'description': 'Это переменные компонентов документа', 'var': Components.true_dict}
            )


