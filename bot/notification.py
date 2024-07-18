import requests

from config import Settings
from database.db_sqlite import select


class Notification:

    @staticmethod
    def send_to_telegram(server, msg):
        settings = Settings(_env_file=f'{server}.env')
        user_id = select('worklog_errors')
        for i in user_id:
            url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendDocument"

            files = {
                'document': open(settings.LOG_PATH, 'rb')
            }
            data = {
                'chat_id': i,
                'caption': msg
            }

            requests.post(url, files=files, data=data)
