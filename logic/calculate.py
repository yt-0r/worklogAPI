import json

import pandas as pd
import time


class Calculator:
    @staticmethod
    def true_date(date_start, date_end):
        time_start = time.strftime('%H %M', time.localtime(date_start))
        time_end = time.strftime('%H %M', time.localtime(date_end))

        res_start = int(time_start[:3]) * 60 + int(time_start[3:])
        res_end = int(time_end[:3]) * 60 + int(time_end[3:])

        return [res_start, res_end]

    @classmethod
    def calc_workers(cls, data):
        data = pd.DataFrame(data)

        workers = data.drop_duplicates(['job_name', 'job_department',
                                        'job_position', 'period_month',
                                        'period_year', 'event', 'work_time',
                                        'day_night', 'work_calendar_day'])

        list_df = []

        for _, worker in workers.iterrows():

            worker_to_calc = data.loc[(data['job_name'] == worker['job_name']) &
                                      (data['job_department'] == worker['job_department']) &
                                      (data['job_position'] == worker['job_position']) &
                                      (data['period_month'] == worker['period_month']) &
                                      (data['period_year'] == worker['period_year']) &
                                      (data['event'] == worker['event']) &
                                      (data['work_time'] == worker['work_time']) &
                                      (data['day_night'] == worker['day_night']) &
                                      (data['work_calendar_day'] == worker['work_calendar_day'])]

            timetracking_to_calc = worker_to_calc['kontrakt_timetracking'].to_list()

            # получаем сырые timetracking на работника
            timetracking_raw = [list(i.values())[0] for i in timetracking_to_calc]

            # timetracking это время в секундах от 1 января 1970, нам с такими числами работать неудобно,
            # поэтому мы переводим unix время во время в минутах, прошедшее от 00:00 текущего дня,
            # timetracking_day содержит это время
            timetracking_day = [cls.true_date(i[0], i[1]) for i in timetracking_raw]

            # здесь мы делим время в день на 60, получая тем самым часы, и пишем в новый список,
            # попутно зануляя все отрицатальные timetracking, чтобы в дальнейшем была полнота данных
            timetracking_hours = list(
                map(lambda x: x if x > 0 else 0.0, [(i[1] - i[0]) / 60 for i in timetracking_day]))

            # делаем массив с нулями на каждую минуту суток
            array_with_ones = [0 for i in range(1440)]

            # Начинаем писать единицы в ячейку по индексу, который соответствует, минуте, где у него была работа.
            # Например: человек работал так [600, 800], [750, 900], [950,1050]
            # массив в диапазоне от 0 до 599 будет содержать нолики, в диапазоне от 600 до 900 будет содержать единички,
            # в диапазоне от 900 до 950 будут нолики, в диапазоне от 950 до 1050 буду единички, после буду нолики.
            # Посчитав все единички в массиве, и разделив их на 60, мы получим сколько реально работал человек в день

            for array in timetracking_day:
                for ind in range(array[0], array[1]):
                    array_with_ones[ind] = 1

            # получаем сколько человек работал в день по всем заявкам и контрактам
            total = array_with_ones.count(1) / 60

            # вычисляем коэффициент, который показывает, на сколько нужно скорректировать время по timetracking
            # берем с главного контракта кол-во часов
            # work_time = float(worker_to_calc['work_time'].loc[worker_to_calc['kontrakt_type'] == 'main'])

            work_time = float(worker_to_calc['work_time'].iloc[0])
            try:
                ratio = 1 / (sum(timetracking_hours) / total) \
                    if total < work_time \
                    else 1 / (sum(timetracking_hours) / work_time)
            except ZeroDivisionError:
                ratio = 0

            # умножаем каждый timetracking на коэффициент, получаем посчитанные данные
            timetracking_counted = [hour * ratio for hour in timetracking_hours]

            new_total = sum(timetracking_counted)

            # списываем часы на основной контракт
            timetracking_counted[0] = work_time - new_total if new_total < work_time else 0

            # округляем
            timetracking_counted = [round(i, 4) for i in timetracking_counted]

            # собираем скалькулированный dataframe
            calculated_df = data.loc[(data['job_name'] == worker['job_name']) &
                                     (data['job_department'] == worker['job_department']) &
                                     (data['job_position'] == worker['job_position']) &
                                     (data['period_month'] == worker['period_month']) &
                                     (data['period_year'] == worker['period_year']) &
                                     (data['event'] == worker['event']) &
                                     (data['work_time'] == worker['work_time']) &
                                     (data['day_night'] == worker['day_night']) &
                                     (data['work_calendar_day'] == worker['work_calendar_day'])].assign(
                kontrakt_timetracking=timetracking_counted)

            # далее нам нужно схлопнуть несколько записей в одну, если человек работал на одном контракте, но в разных заявках
            # получаем список контрактов работника и бежим по нему

            kontrakts = calculated_df.drop_duplicates('kontrakt_name')['kontrakt_name'].to_list()

            list_df_kontrakts = []

            for kontrakt in kontrakts:
                # считаем сумму timetracking на одном контракте
                sum_timetracking = sum(
                    calculated_df.loc[calculated_df['kontrakt_name'] == kontrakt]['kontrakt_timetracking'].to_list())

                # пишем в новый датафрейм и удаляем дубликаты
                temp_df = (calculated_df.loc[calculated_df['kontrakt_name'] == kontrakt]
                           .assign(kontrakt_timetracking=sum_timetracking)
                           .drop_duplicates())

                # добавляем в лист конкатенации
                list_df_kontrakts.append(temp_df)

            list_df.append(pd.concat(list_df_kontrakts, ignore_index=True))
        return list(pd.concat(list_df, ignore_index=True).to_dict('index').values())