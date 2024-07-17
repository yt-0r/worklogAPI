from typing import Any, Optional, Dict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_REST: str
    LOG_PATH: str
    DB_USER: str
    DB_PASS: str
    DB_PORT: str
    DB_NAME: str
    DOC_NAME: str
    DOC_PATH: str
    DOC_TYPE: str
    FTP_USER: str
    FTP_PASS: str

    def DATABASE_URL_mysqlconnector(self, url):
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASS}@{url}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings(_env_file='jiradev.env')

# http://jiradev.its-sib.ru/rest/scriptrunner/latest/custom/reportBackup?query=getNew&date=
# http://jira.its-sib.ru/rest/scriptrunner/latest/custom/getStaffWorklog?query=getNew&date=
