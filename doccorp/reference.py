class Reference:
    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.short_id = record['id'].split('_')[-1]
        self.name = record['name']

        val: str

        if 'value' in record:
            val = f"Справка-вызов №: {record['value']}" if record['value'] != 'null' else ''
        else:
            val = record['name']

        val = val.replace('\\', '')
        self.value = val

        Reference.true_list.append({'id': self.id,
                                    'var': f'var_{self.short_id}',
                                    'name': self.name,
                                    'value': self.value})
