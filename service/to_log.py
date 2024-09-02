import logging
from config import Settings


class Logging:
    @staticmethod
    def log_set(filename):
        logging.basicConfig(filename=filename,
                            filemode='w',
                            format='[%(asctime)s] [%(levelname)s] => %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO,
                            encoding='utf-8'
                            )

    @staticmethod
    def log_add(lv, message):
        logging.log(level=lv, msg=message)
