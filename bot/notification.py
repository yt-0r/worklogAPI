import requests

from config import Settings
from bot.db_sqlite import select


class Notification:

    @staticmethod
    def send_to_telegram(server, msg, kind):
        settings = Settings(_env_file=f'{server}.env')
        if kind == 'doc':
            user_id = select('doccorp_errors')
            doc = 'doc'
        elif kind == 'red':
            user_id = select('redirect_errors')
            doc = 'redirect'

        elif kind == 'book':
            user_id = select('worklog_errors')
            doc = f'{server}_worklog'

        else:
            user_id = select('worklog_errors')
            doc = 'all'

        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendDocument"
        for i in user_id:
            files = {
                'document': open(f'{settings.LOG_PATH}/{doc}.log', 'rb')
            }
            data = {
                'chat_id': i,
                'caption': msg
            }
            requests.post(url, files=files, data=data)
