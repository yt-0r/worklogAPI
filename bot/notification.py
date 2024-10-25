import requests

from config import Settings
from database.db_sqlite import select


class Notification:

    @staticmethod
    def send_to_telegram(server, msg):
        settings = Settings(_env_file=f'{server}.env')

        # выбираем юзеров, которые подписаны на рассылку worklog_errors
        user_id = select('worklog_errors')
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendDocument"
        for i in user_id:
            files = {
                'document': open(f'{settings.LOG_PATH}/all.log', 'rb')
            }
            data = {
                'chat_id': i,
                'caption': msg
            }

            requests.post(url, files=files, data=data)
