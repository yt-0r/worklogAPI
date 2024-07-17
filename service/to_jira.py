# Стандартные библиотеки
import os
# Сторонние библиотеки
from jira import JIRA
from config import Settings
from fastapi import Body
from fastapi.responses import FileResponse
from ftplib import FTP


class Jira:

    @staticmethod
    def attach(url, server, name):
        settings = Settings(_env_file=f'{server}.env')

        ftp = FTP(url.split('//')[1])
        ftp.login(user=settings.FTP_USER, passwd=settings.FTP_PASS)

        ftp.cwd('scripts/DIRECTORY/POSTFUNCTIONS/STAFF/WORKLOG/')

        with open(name, 'rb') as file:
            ftp.storbinary(f'STOR {name}', file)

        ftp.close()
