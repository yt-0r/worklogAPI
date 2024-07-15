import logging

import requests
from sqlalchemy import select, delete
from sqlalchemy.orm import sessionmaker

from database.sql import sql_set, Base

import pandas as pd

import hashlib


class SyncORM:
    @staticmethod
    def insert_data(data, model, server):
        sync_session_factory = sessionmaker(sql_set(server=server))
        with sync_session_factory() as session:
            workers = [model(
                id=hashlib.md5((json[0]['job_name'] + ' ' +
                                json[0]['job_department'] + ' ' +
                                json[0]['job_position'] + ' ' +
                                json[0]['period_month'] + ' ' +
                                str(json[0]['period_year'])).encode()).hexdigest(),
                job_name=json[0]['job_name'],
                job_department=json[0]['job_department'],
                job_position=json[0]['job_position'],
                period_month=json[0]['period_month'],
                period_year=json[0]['period_year'],
                json_worker=json) for json in data
            ]

            [session.add(worker) for worker in workers]
            session.commit()

    @staticmethod
    def create_table(server):

        Base.metadata.create_all(sql_set(server))

    @staticmethod
    def delete_data(data, model, server):
        dataframe_from_json = pd.DataFrame(data)
        sync_session_factory = sessionmaker(sql_set(server=server))
        with sync_session_factory() as session:
            stmt = delete(model).where(
                model.period_month.in_(dataframe_from_json['period_month'].drop_duplicates().to_list()),
                model.job_name.in_(dataframe_from_json['job_name'].drop_duplicates().to_list()),
                model.period_year.in_(dataframe_from_json['period_year'].drop_duplicates().to_list()),
                model.job_position.in_(dataframe_from_json['job_position'].drop_duplicates().to_list()),
                model.job_department.in_(dataframe_from_json['job_department'].drop_duplicates().to_list())
            )

            session.execute(stmt)
            session.commit()

    @staticmethod
    def select_data(data, model, server):
        dataframe_from_json = pd.DataFrame(data)
        sync_session_factory = sessionmaker(sql_set(server=server))
        with sync_session_factory() as session:
            stmt = select(model).where(
                model.period_month.in_(dataframe_from_json['period_month'].drop_duplicates().to_list()),
                model.job_name.in_(dataframe_from_json['job_name'].drop_duplicates().to_list()),
                model.period_year.in_(dataframe_from_json['period_year'].drop_duplicates().to_list()),
                model.job_position.in_(dataframe_from_json['job_position'].drop_duplicates().to_list()),
                model.job_department.in_(dataframe_from_json['job_department'].drop_duplicates().to_list())
            )

        results = session.execute(stmt).scalars().all()
        dict_from_database = [result.__dict__ for result in results]
        [x.pop('_sa_instance_state') for x in dict_from_database]

        try:
            true_dict = list(pd.concat(
                [df for df in [pd.DataFrame(record['json_worker']) for record in dict_from_database]],
                ignore_index=True).to_dict('index').values())
        except ValueError:
            true_dict = []

        return true_dict

    @staticmethod
    def select_year(model, year, server):
        sync_session_factory = sessionmaker(sql_set(server=server))
        with sync_session_factory() as session:
            stmt = select(model).where(model.period_year.in_([year]))
        results = session.execute(stmt).scalars().all()

        dict_from_database = [result.__dict__ for result in results]
        [x.pop('_sa_instance_state') for x in dict_from_database]

        try:
            true_dict = list(pd.concat(
                [df for df in [pd.DataFrame(record['json_worker']) for record in dict_from_database]],
                ignore_index=True).to_dict('index').values())
        except ValueError:
            true_dict = []

        return true_dict
