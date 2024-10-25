class TrueDate:
    month_dict = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля",
                  8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}

    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.name = record['name']
        self.short_id = record['id'].split('_')[-1]

        val: str

        if 'value' in record:
            self.date_list = record['value'].split(' ')[0].split('-') if record['value'] != 'null' else ['', '', '']
        else:
            self.date_list = ['01', '01', '1970']

        self.__format_date_1()
        self.__format_date_2()

    def __format_date_1(self):
        day = self.date_list[-1]
        month = self.date_list[1]
        year = self.date_list[0]

        if self.date_list != ['', '', '']:
            format_date_1 = f'{int(day)} {TrueDate.month_dict[int(month)]} {year}'
        else:
            format_date_1 = ''

        TrueDate.true_list.append({'id': self.id,
                                   'var': f'format1_{self.short_id}',
                                   'name': self.name,
                                   'value': format_date_1})

    def __format_date_2(self):
        day = self.date_list[-1]
        month = self.date_list[1]
        year = self.date_list[0]

        if self.date_list != ['', '', '']:
            format_date_2 = f'{day}.{month}.{year}'
        else:
            format_date_2 = ''

        TrueDate.true_list.append({'id': self.id,
                                   'var': f'format2_{self.short_id}',
                                   'name': self.name,
                                   'value': format_date_2})
