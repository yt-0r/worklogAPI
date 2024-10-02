class TrueDate:
    month_dict = {1: "января", 2: "февраля", 3: "марта", 4: "апреля", 5: "мая", 6: "июня", 7: "июля",
                  8: "августа", 9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"}

    true_dict = {}

    def __init__(self, date, var):
        self.true_list = []
        self.var = var
        self.date = '1970.01.01' if date is None else date
        self.date_list = self.date.split('.')
        self.__format_date_1()
        self.__format_date_2()

    def __format_date_1(self):
        day = self.date_list[-1]
        month = self.date_list[1]
        year = self.date_list[0]
        format_date_1 = f'{int(day)} {TrueDate.month_dict[int(month)]} {year}'

        TrueDate.true_dict[f'{self.var}_format1'] = format_date_1

    def __format_date_2(self):
        day = self.date_list[-1]
        month = self.date_list[1]
        year = self.date_list[0]

        format_date_2 = f'{day}.{month}.{year}'
        TrueDate.true_dict[f'{self.var}_format2'] = format_date_2

