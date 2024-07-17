import requests

from config import Settings


def send_to_telegram(server, user_id, document, msg):
    settings = Settings(_env_file=f'{server}.env')
    for i in user_id:
        url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/sendDocument"

        files = {
            'document': open(document, 'rb')
        }
        data = {
            'chat_id': i,
            'caption': msg
        }

        requests.post(url, files=files, data=data)


bot_token = '7256671211:AAGTZKYiVcg_y3jfvBBqtBXLHilIwG7he3Q'
chat_id = [2058516705, 5548471233]
document_path = 'worklog.log'  # Путь к файлу, который хотите отправить
caption = 'пиздец!'

send_to_telegram(bot_token, chat_id, document_path, caption)
