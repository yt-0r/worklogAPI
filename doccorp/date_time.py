import json
from datetime import datetime


class DateTime:
    month_dict = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля",
                  8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}

    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.name = record['name']
        self.short_id = record['id'].split('_')[-1]

        if 'value' in record:
            date_list = record['value'].split(' ')[0].split('-') if record['value'] != 'null' else ['', '', '']
            time_list = record['value'].split(' ')[-1].split('.')[0].split(':') if record['value'] != 'null' else ['',
                                                                                                                   '',
                                                                                                                   '']
        else:
            date_list = ['1970', '01', '01']
            time_list = ['00', '00', '00']

        self.day = date_list[-1]
        self.month = date_list[1]
        self.year = date_list[0]
        self.hour = time_list[0]
        self.minute = time_list[1]

        if date_list != ['', '', '']:
            self.__format_date_1()
            self.__format_date_2()
            self.__format_date_3()
            self.__format_date_4()

    def __format_date_1(self):
        format_date_1 = f'{int(self.day)} {DateTime.month_dict[int(self.month)]} {self.year}'
        DateTime.true_list.append({'id': self.id,
                                   'var': f'form1_{self.short_id}',
                                   'name': self.name,
                                   'value': format_date_1})

    def __format_date_2(self):
        format_date_2 = f'{self.day}.{self.month}.{self.year}'
        DateTime.true_list.append({'id': self.id,
                                   'var': f'form2_{self.short_id}',
                                   'name': self.name,
                                   'value': format_date_2})

    def __format_date_3(self):
        format_date_3 = f'{self.hour}:{self.minute} ч. {self.day}.{self.month}.{self.year}г.'
        DateTime.true_list.append({'id': self.id,
                                   'var': f'form3_{self.short_id}',
                                   'name': self.name,
                                   'value': format_date_3})

    def __format_date_4(self):
        with open('jsons/calendar.json', 'r', encoding='utf-8') as file:
            calendar = json.load(file)
            list_weekends = calendar['weekends']
            list_workings = calendar['workings']

        merge_date = '.'.join([self.day, self.month, self.year])
        day_week = datetime.strptime(merge_date, "%d.%m.%Y").weekday()
        type_permit = ''

        if day_week in [5, 6] or merge_date in list_weekends:
            type_permit = 'выходной день'
        if day_week not in [5, 6] or merge_date in list_workings:
            type_permit = 'вечернее/ночное время'

        DateTime.true_list.append({'id': self.id,
                                   'var': f'form4_{self.short_id}',
                                   'name': self.name,
                                   'value': type_permit})
