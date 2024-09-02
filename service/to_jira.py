from config import Settings
from ftplib import FTP



class Jira:

    @staticmethod
    def attach(url, server, name):
        settings = Settings(_env_file=f'{server}.env')

        ftp = FTP(settings.JIRA_SERVER)
        ftp.login(user=settings.FTP_USER, passwd=settings.FTP_PASS)

        directory = 'jira/scripts/DIRECTORY/POSTFUNCTIONS/STAFF/WORKLOG' if server == 'jira' \
            else 'scripts/DIRECTORY/POSTFUNCTIONS/STAFF/WORKLOG'

        ftp.cwd(directory)

        true_name = name.split('/')[-1]
        with open(name, 'rb') as file:
            ftp.storbinary(f'STOR {true_name}', file)

        ftp.close()
