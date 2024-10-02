from pytrovich.enums import NamePart, Gender, Case
from pytrovich.maker import PetrovichDeclinationMaker
from pymorphy3 import MorphAnalyzer


class PymorphyPos:
    position_dict = {'managerPosition': 'руководитель', 'workerPosition': 'работник', 'bossPosition': 'директор'}
    true_dict = {}

    def __init__(self, position, var):
        self.var = var
        self.position = PymorphyPos.position_dict[self.var] if position is None else position
        self.__nominative_case_position()
        self.__dative_case_position()
        self.__parent_case_position()

    def __dative_case_position(self):
        PymorphyPos.true_dict[f'{self.var}_dativeCase'] = self.__declination(position=self.position, case=Case.DATIVE)

    def __parent_case_position(self):
        PymorphyPos.true_dict[f'{self.var}_parentCase'] = self.__declination(position=self.position, case=Case.GENITIVE)

    def __nominative_case_position(self):
        PymorphyPos.true_dict[f'{self.var}_nominative'] = f'{self.position[0].lower()}{self.position[1:]}'

    @staticmethod
    def __declination(position, case):
        maker = PetrovichDeclinationMaker()
        morph = MorphAnalyzer()
        words_pos = position.split(' ')
        inclined_word = ''

        for word in words_pos:
            if '-' in word:
                # слово до дефиса
                word_before = word.split('-')[0]
                # слово после дефиса
                word_after = word.split('-')[-1]

                # обработка первой части слова
                if word_before.isupper() or word_before.isdigit() or word_before == 'Офис':  # отсекаем аббревиатуры,
                    word_before = 'офис' if word_before == 'Офис' else word_after
                    inclined_word = inclined_word + word_before + '-'
                else:
                    word_pymorph = morph.parse(word_before)[0].normal_form
                    inclined_word = inclined_word + maker.make(NamePart.LASTNAME, Gender.MALE, case, word_pymorph) + '-'

                # обработка второй части слова
                if word_after.isupper() or word_after.isdigit():  # отсекаем аббревиатуры, числа
                    inclined_word = inclined_word + word_after
                else:
                    word_pymorph = morph.parse(word_after)[0].normal_form
                    inclined_word = inclined_word + maker.make(NamePart.LASTNAME, Gender.MALE, case, word_pymorph)
                inclined_word = inclined_word + ' '

            elif word.isupper() or word.isdigit():  # отсекаем аббревиатуры, числа, уже редактированные слова
                inclined_word = inclined_word + word + ' '

            elif word.isupper() is False or word.isdigit is False:  # склоняем оставшиеся слова
                word_pymorph = morph.parse(word)[0].normal_form
                inclined_word = inclined_word + maker.make(NamePart.LASTNAME, Gender.MALE, case, word_pymorph) + ' '

        return inclined_word
