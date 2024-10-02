from translate import Translator


class Components:
    true_dict = {}

    def __init__(self, field, var):
        self.var = var
        self.field = var if field is None else field
        self.__append()

    def __append(self):
        Components.true_dict[f'{self.var}'] = self.field
