class Sign:
    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.short_id = record['id'].split('_')[-1]
        self.name = record['name']
        self.value = record['value'] if 'value' in record else record['name']

        self.__sign()
        # self.__manager()
        # self.__worker()

    def __sign(self):
        Sign.true_list.append({'id': self.id,
                               'var': f'sign_{self.short_id}',
                               'name': self.name,
                               'value': self.value})
