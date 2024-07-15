from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase, mapped_column, Mapped
from sqlalchemy import URL, create_engine, text

from config import Settings


def sql_set(server):
    settings = Settings(_env_file=f'{server}.env')

    sync_engine = create_engine(
        url=settings.DATABASE_URL_mysqlconnector,
        # echo=True,
        # pool_size=5,
        # max_overflow=10,
    )

    return sync_engine


class Base(DeclarativeBase):
    pass
