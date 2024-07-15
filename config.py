from typing import Any, Optional, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ZABBIX_USER: str
    ZABBIX_PASSWORD: str
    JIRA_REST: str
    SERVICE_REST: str
    LOG_PATH: str
    # FILE_PATH: str
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DOC_NAME: str
    DOC_PATH: str
    DOC_TYPE: str
    JIRA_SERVER: str
    ISSUE_KEY: str

    @property
    def DATABASE_URL_mysqlconnector(self):
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings(_env_file='dev.env')


# def true_server(serv):
#     global settings
#     settings = Settings(_env_file='dev.env') if serv == 'dev' else Settings(_env_file='prd.env')
#     return settings

# http://jiradev.its-sib.ru/rest/scriptrunner/latest/custom/reportBackup?query=getNew&date=
# http://jira.its-sib.ru/rest/scriptrunner/latest/custom/getStaffWorklog?query=getNew&date=
