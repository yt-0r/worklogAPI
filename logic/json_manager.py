import logging
import traceback
from json import dumps, loads
import pandas as pd
import requests

from config import Settings


class JsonManager:
    @staticmethod
    def merge(data_from_json, data_from_database, server):

        settings = Settings(_env_file=f'{server}.env')

        try:
            df_from_json = pd.DataFrame(data_from_json)

            df_from_database = pd.DataFrame(data_from_database)

            # делаем из kontrakt_timetracking строку
            df_from_database['kontrakt_timetracking'] = df_from_database['kontrakt_timetracking'].apply(
                lambda x: dumps(x))
            df_from_json['kontrakt_timetracking'] = df_from_json['kontrakt_timetracking'].apply(lambda x: dumps(x))

            # удаляем дубликаты
            df_from_json = df_from_json.drop_duplicates()
            df_from_database = df_from_database.drop_duplicates()

            # меняем порядок столбцов фрейма из базы данных
            df_from_database = df_from_database[[column_name for column_name in df_from_json]]

            # начинаем мерджить
            raw_merge = pd.merge(df_from_json, df_from_database,
                                 on=['day_night', 'work_calendar_day', 'work_calendar_daytype', 'job_name',
                                     'job_department',
                                     'job_position', 'period_month', 'period_year', 'kontrakt_name', 'kontrakt_type',
                                     'kontrakt_issuecount', 'kontrakt_filter'], indicator='ind', how='outer')

            merge_both_and_left = (raw_merge.loc[raw_merge['ind'] != 'right_only']
                                   .rename(columns=
                                           {'event_x': 'event',
                                            'work_time_x': 'work_time',
                                            'kontrakt_timetracking_x': 'kontrakt_timetracking',
                                            }).
                                   drop(['event_y', 'work_time_y', 'kontrakt_timetracking_y'], axis=1))

            merge_right = (raw_merge.loc[raw_merge['ind'] == 'right_only']
                           .rename(columns=
                                   {'event_y': 'event',
                                    'work_time_y': 'work_time',
                                    'kontrakt_timetracking_y': 'kontrakt_timetracking',
                                    }).
                           drop(['event_x', 'work_time_x', 'kontrakt_timetracking_x'], axis=1))

            result_df = pd.concat([merge_both_and_left, merge_right], ignore_index=True).drop('ind', axis=1)

            # делаем обратно словарь
            result_df['kontrakt_timetracking'] = result_df['kontrakt_timetracking'].apply(lambda x: loads(x))

            # requests.get(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message=nice!')
            return result_df

        except ValueError as er:
            requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message={traceback.format_exc()}')
            return pd.DataFrame(data_from_json)

        except KeyError as er:
            requests.post(f'{settings.SERVICE_REST}/service/log?level={logging.INFO}&message={traceback.format_exc()}')
            return pd.DataFrame(data_from_json)

    @staticmethod
    def group(data):
        # получаем список работников
        workers = data.drop_duplicates(['job_name', 'job_department', 'job_position', 'period_month', 'period_year'])

        group_data = []

        # группируем по сотрудникам
        for index, row in workers.iterrows():
            group_data.append(list(data.loc[(data['job_name'] == row['job_name']) &
                                            (data['job_department'] == row['job_department']) &
                                            (data['job_position'] == row['job_position']) &
                                            (data['period_month'] == row['period_month']) &
                                            (data['period_year'] == row['period_year'])].to_dict('index').values()))

        return group_data
