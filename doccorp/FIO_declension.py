from pytrovich.detector import PetrovichGenderDetector
from pytrovich.enums import NamePart, Case
from pytrovich.maker import PetrovichDeclinationMaker


class PytrovichFIO:
    true_list = []

    def __init__(self, record):
        self.id = record['id']
        self.short_id = record['id'].split('_')[-1]
        self.name = record['name']
        self.value = record['value'].split('_pk_')[0] if 'value' in record else 'Иванов Иван Иванович'
        self.__nominative_case_long()
        self.__nominative_case_short()
        self.__parent_case_long()
        self.__parent_case_short()
        self.__dative_case_long()
        self.__dative_case_short()

    def __nominative_case_long(self):
        PytrovichFIO.true_list.append({'id': self.id,
                                       'var': f'nominat_{self.short_id}',
                                       'name': self.name,
                                       'value': self.value})

    def __parent_case_long(self):
        PytrovichFIO.true_list.append({'id': self.id,
                                       'var': f'parent_{self.short_id}',
                                       'name': self.name,
                                       'value': self.__pytrovich(name=self.value, case=Case.GENITIVE)})

    def __dative_case_long(self):
        PytrovichFIO.true_list.append({'id': self.id,
                                       'var': f'dative_{self.short_id}',
                                       'name': self.name,
                                       'value': self.__pytrovich(name=self.value, case=Case.DATIVE)})

    def __nominative_case_short(self):
        temp_name = self.value
        first_name = temp_name.split(' ')[1]
        last_name = temp_name.split(' ')[0]
        middle_name = temp_name.split(' ')[-1]

        PytrovichFIO.true_list.append({'id': self.id,
                                       'var': f'short1_{self.short_id}',
                                       'name': self.name,
                                       'value': f'{last_name} {first_name[0]}.{middle_name[0]}'})

    def __parent_case_short(self):
        temp_name = self.__pytrovich(name=self.value, case=Case.GENITIVE)
        first_name = temp_name.split(' ')[1]
        last_name = temp_name.split(' ')[0]
        middle_name = temp_name.split(' ')[-1]

        PytrovichFIO.true_list.append({'id': self.id,
                                       'var': f'short2_{self.short_id}',
                                       'name': self.name,
                                       'value': f'{last_name} {first_name[0]}.{middle_name[0]}'})

    def __dative_case_short(self):
        temp_name = self.__pytrovich(name=self.value, case=Case.DATIVE)
        first_name = temp_name.split(' ')[1]
        last_name = temp_name.split(' ')[0]
        middle_name = temp_name.split(' ')[-1]

        PytrovichFIO.true_list.append({'id': self.id,
                                       'var': f'short3_{self.short_id}',
                                       'name': self.name,
                                       'value': f'{last_name} {first_name[0]}.{middle_name[0]}'})



    @staticmethod
    def __pytrovich(name, case):
        first_name = name.split(' ')[1]
        last_name = name.split(' ')[0]
        middle_name = name.split(' ')[-1]

        detector = PetrovichGenderDetector()
        # выясняем пол
        sex = detector.detect(firstname=first_name, lastname=last_name, middlename=middle_name)

        # склоняем
        maker = PetrovichDeclinationMaker()
        true_name = (
            f'{maker.make(name_part=NamePart.LASTNAME, gender=sex, case_to_use=case, original_name=last_name)} '
            f'{maker.make(name_part=NamePart.FIRSTNAME, gender=sex, case_to_use=case, original_name=first_name)} '
            f'{maker.make(name_part=NamePart.MIDDLENAME, gender=sex, case_to_use=case, original_name=middle_name)}')

        return true_name
