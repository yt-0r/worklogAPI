import logging
from config import Settings


class Logging:
    @staticmethod
    def log_set(server):
        settings = Settings(_env_file=f'{server}.env')
        logging.basicConfig(filename=settings.LOG_PATH,
                            filemode='w',
                            format='[%(asctime)s] [%(levelname)s] => %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S',
                            level=logging.INFO,
                            encoding='utf-8'
                            )

    @staticmethod
    def log_add(lv, message):
        logging.log(level=lv, msg=message)
