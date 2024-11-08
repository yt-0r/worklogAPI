import logging
from config import Settings


class Logging:

    my_loger = None

    @classmethod
    def __init__(cls, cfg):
        cls.my_loger = logging.getLogger(cfg)

    @staticmethod
    def log_add(lv, message):
        Logging.my_loger.log(level=lv, msg=message)
