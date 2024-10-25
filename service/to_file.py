import json


class JsonFile:
    @staticmethod
    def record(data, file_name='.json'):
        # Запись данных в файл JSON
        file_name = f'jsons/{file_name}'
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=2)
