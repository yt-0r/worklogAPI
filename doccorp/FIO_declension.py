from pytrovich.detector import PetrovichGenderDetector
from pytrovich.enums import NamePart, Case
from pytrovich.maker import PetrovichDeclinationMaker


class PytrovichFIO:

    names = {'worker': 'Иванов Иван Иванович', 'boss': 'Петров Петр Петрович', 'manager': 'Алексеев Алексей Алексеевич'}
    true_dict = {}

    def __init__(self, name, var):

        self.var = var
        self.full_name = PytrovichFIO.names[var] if name is None else name
        self.__nominative_case_long()
        self.__nominative_case_short()
        self.__parent_case_long()
        self.__parent_case_short()
        self.__dative_case_long()
        self.__dative_case_short()

    def __nominative_case_long(self):
        PytrovichFIO.true_dict[f'{self.var}_fullName'] = self.full_name

    def __parent_case_long(self):
        PytrovichFIO.true_dict[f'{self.var}_parentCaseLongName'] = self.__pytrovich(name=self.full_name, case=Case.GENITIVE)

    def __dative_case_long(self):
        PytrovichFIO.true_dict[f'{self.var}_dativeCaseLongName'] = self.__pytrovich(name=self.full_name, case=Case.DATIVE)

    def __nominative_case_short(self):
        temp_name = self.full_name
        first_name = temp_name.split(' ')[1]
        last_name = temp_name.split(' ')[0]
        middle_name = temp_name.split(' ')[-1]

        PytrovichFIO.true_dict[f'{self.var}_fullNameShort'] = f'{last_name} {first_name[0]}.{middle_name[0]}'

    def __parent_case_short(self):
        temp_name = self.__pytrovich(name=self.full_name, case=Case.GENITIVE)
        first_name = temp_name.split(' ')[1]
        last_name = temp_name.split(' ')[0]
        middle_name = temp_name.split(' ')[-1]

        PytrovichFIO.true_dict[f'{self.var}_parentCaseShortName'] = f'{last_name} {first_name[0]}.{middle_name[0]}'

    def __dative_case_short(self):
        temp_name = self.__pytrovich(name=self.full_name, case=Case.DATIVE)
        first_name = temp_name.split(' ')[1]
        last_name = temp_name.split(' ')[0]
        middle_name = temp_name.split(' ')[-1]

        PytrovichFIO.true_dict[f'{self.var}_dativeCaseShortName'] = f'{last_name} {first_name[0]}.{middle_name[0]}'

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
