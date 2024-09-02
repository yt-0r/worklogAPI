from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import create_engine

from config import Settings


def sql_set(server, url):
    settings = Settings(_env_file=f'{server}.env')
    sync_engine = create_engine(
        url=settings.DATABASE_URL_mysqlconnector(host=settings.JIRA_SERVER)
    )

    return sync_engine


class Base(DeclarativeBase):
    pass
