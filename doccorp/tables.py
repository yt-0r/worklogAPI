class Tables:
    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.short_id = record['id'].split('_')[-1]
        self.name = record['name']

        if 'value' in record:
            self.value = self.__run(record['value'])
        else:
            self.value = record['name']

        self.__table()
        self.__strTable()

    def __strTable(self):
        try:
            join_str = ' ,'.join([val['col1'] for val in self.value])
        except TypeError:
            join_str = ''
        Tables.true_list.append({'id': self.id,
                                 'var': f'str_{self.short_id}',
                                 'name': f'{self.name}(1 колонка в виде строки)',
                                 'value': join_str})

    def __table(self):
        Tables.true_list.append({'id': self.id,
                                 'var': f'p table_{self.short_id}',
                                 'name': self.name,
                                 'value': self.value})

    @staticmethod
    def __run(table: str):

        table = table.replace(' ', ' ')
        row_list = table.split('||')[-1].split('|')

        while '\r\n' in row_list:
            row_list.remove('\r\n')

        row_list = row_list[:-1]

        n = len(table.split('||')) - 2
        n_list = [i for i in range(n)]

        group_list = []
        for i in range(0, len(row_list), n):
            group_list.append([row_list[i + j] for j in n_list])

        end_list = []
        for i, arr in enumerate(group_list):
            temp_dict = {}
            for j, element in enumerate(arr):
                temp_dict[f'col{j}'] = element
            end_list.append(temp_dict)

        return end_list
