class Contracts:
    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.short_id = record['id'].split('_')[-1]
        self.name = record['name']
        self.value = record['value'] if 'value' in record.keys() else 'Контракт № 777 - ТУАД_pk_Контракт № 777 - ТУАД"'
        self.__parse()

    def __parse(self):
        # парсим контракты
        contracts = [contract.split('_pk_')[0] for contract in self.value.split('###')]

        # срезаем названия контрактов если те больше 40 символов
        contracts = [contract if len(contract) < 50 else contract[:50] + '...' for contract in contracts]

        # если контрактов больше 5, ты выводим только их названия
        if len(contracts) > 5:
            contracts = ', '.join(f"{contract.split(' ')[1]} {contract.split(' ')[2]}" for contract in contracts)

        else:
            contracts = '\n'.join(contracts)

        Contracts.true_list.append({'id': self.id,
                                    'var': f'var_{self.short_id}',
                                    'name': self.name,
                                    'value': contracts})
