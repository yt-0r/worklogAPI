class System:
    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.short_id = record['id'].split('_')[-1]
        self.name = record['name']

        if 'value' in record:
            val = record['value'] if record['value'] != 'null' else ''
        else:
            val = record['name']

        val = val.replace('\\', '')

        self.value = val

        System.true_list.append({'id': self.id,
                                 'var': f'var_{self.short_id}',
                                 'name': self.name,
                                 'value': self.value})
