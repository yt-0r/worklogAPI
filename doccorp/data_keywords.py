# Этот файл занимается подготовкой словаря с значениями для вставки в документ
# принимает в качестве параметров строку на рестАПИ заявки, учетную запись пользователя из под которого будет вся эта кухня выполняться и данные пользователя для вставки в документ

import sys

sys.path.append("../")  #здесь нужно прописать путь к папке, где лежат скрипты, которые мы подключаем
from re import template
from textwrap import TextWrapper, dedent
import configparser


# # ========================= подключаем config =============================
# config = configparser.ConfigParser()  # создаём объекта парсера
# config.read(arg['config_path'])  # читаем конфиг arg['config_path']
# # =========================================================================
# #здесь указан путь к папке, где лежит jira_connect.py коннект к Жыре
# sys.path.append(config['scrypts_path']['path_jira']) 
# import jira_connect




def num_month(date_list):  # здесь переделываем номер месяца в название
    month = [' ', 'Января', 'Февраля', 'Марта', 'Апреля', 'Мая', 'Июня', 'Июля', 'Августа', 'Сентября', 'Октября',
             'Ноября', 'Декабря']
    date_list[1] = date_list[1].replace(date_list[1], month[int(date_list[1])])  #подменяем цифру месяца на название
    return date_list


#----------------------------------------------

class DataKeywords:
    @classmethod
    def data(cls, issue, login='none', password='none', config_path='none'):




        # здесь получаем данные с полей и читим от мусора, что бы получилась нормальная строка
        data_smeta = {}  #создаем словарь
        #Контракт--------

        fucking_list = ['timespent', 'customfield_17501', 'project', 'customfield_15200', 'customfield_17500', 'fixVersions', 'customfield_15201', 'resolution', 'customfield_11400',
                        'resolutiondate', 'customfield_16807', 'workratio', 'watches', 'customfield_10065', 'customfield_11701', 'customfield_14818', 'customfield_14819', 'issuelinks',
                        'assignee', 'status', 'customfield_14810', 'customfield_15700', 'customfield_17800', 'attachment', 'creator', 'reporter', 'customfield_11405', 'customfield_11405',
                        'component', 'votes', 'worklog'
                        ]

        for delete in fucking_list:
            issue['fields'].pop(delete)

        print(issue)

        if 'customfield_11600' in issue['fields'] and issue['fields']['customfield_11600'] != None:
            contract = issue['fields']['customfield_11600'].split(
                "_pk_")  # следующая куча иф ов сокращает название контракта как может и пилит его по ближайшему к 36 символам пробелу. далее делаем список из двух элементов
            contract = contract[0]
            c_find = 'Контракт '
            if c_find in contract:
                contract = contract.replace(c_find, '')

            #ограничение в 36 символов на строке
            if len(contract) > 37:
                num = contract.rfind(' ', 0, 37)
                new_character = '|'
                contract = contract[:num] + new_character + contract[num + 1:]
                contract = contract.split("|")
            data_smeta['contract'] = contract

            contract = issue['fields']['customfield_11600']
            if contract.find('_pk_') > -1:
                contract = issue['fields']['customfield_11600'].split("_pk_")
                contract = contract[0]
            data_smeta['contract_metrology'] = contract

        #----------------
        # номер заявки, которую мы отрабатываем
        if issue['key']:
            issuekey = issue['key']
            data_smeta['issuekey'] = issuekey
            # --------------------------------------
        #Контракт--------

        if 'customfield_14909' in issue['fields']:
            contract = issue['fields']['customfield_14909'].split(
                "_pk_")  # следующая куча ифов сокращает название контракта как может и пилит его по ближайшему к 36 символам пробелу. далее делаем список из двух элементов

            contract = contract[0]

            c_find = 'Контракт '
            if c_find in contract:
                contract = contract.replace(c_find, '')
            data_smeta['contract_ower_all'] = contract.replace('Контракт ', '')
            # print('contract-->>', contract)
            #ограничение в 36 символов на строке
            if len(contract) > 37:
                num = contract.rfind(' ', 0, 37)
                new_character = '|'
                contract = contract[:num] + new_character + contract[num + 1:]
                contract = contract.split("|")

            data_smeta['contract_ower'] = contract
            data_smeta['contracts_owerwork'] = contract
            if issue['fields']['customfield_14909'].find('###') != -1:
                contractsall = []
                contractsalltmp = issue['fields']['customfield_14909'].split('###')
                for con in contractsalltmp:
                    contractsall.append(con.split('_pk_')[0].replace('Контракт ', ''))
                data_smeta['contracts_owerwork'] = contractsall

                #----------------
        #Расход по смете------
        if 'customfield_14806' in issue['fields']:
            total_rub = issue['fields']['customfield_14806'].split("|")
            total_rub = str(total_rub[len(total_rub) - 2])
            data_smeta['total_rub'] = total_rub
            #---------------------
        #Название организации
        if 'customfield_14846' in issue['fields']:
            company = issue['fields']['customfield_14846']
            data_smeta['company'] = company
            #---------------------
        #ФИО Директора--------
        if 'customfield_14907' in issue['fields'] and issue['fields']['customfield_14907'] != None:
            boss = issue['fields']['customfield_14907']

            boss = boss.split(" ")
            data_smeta['boss'] = boss
        #---------------------
        #На производство работ в пунктах
        if 'customfield_14813' in issue['fields']:
            dislocation = issue['fields']['customfield_14813']
            data_smeta['dislocation'] = dislocation
        #---------------------
        #Порученных (Командируемое лицо)
        if 'customfield_14809' in issue['fields']:
            traveler = issue['fields']['customfield_14809']
            data_smeta['traveler'] = traveler
        #---------------------
        #Дата начала командировки
        if 'customfield_14801' in issue['fields'] and issue['fields']['customfield_14801'] != None:
            start_trip = issue['fields']['customfield_14801'].split("-")
            num_month(start_trip)
            data_smeta['start_trip'] = start_trip
        #---------------------
        #Дата окончания командировки
        if 'customfield_14802' in issue['fields'] and issue['fields']['customfield_14802'] != None:
            end_trip = issue['fields']['customfield_14802'].split("-")
            num_month(end_trip)
            data_smeta['end_trip'] = end_trip
        #---------------------
        #Дата заполнения сметы
        if 'created' in issue['fields']:
            date_smeta = issue['fields']['created'][0:10].split("-")
            num_month(date_smeta)
            data_smeta['date_smeta'] = date_smeta

            date_smeta_num = issue['fields']['created'][0:10].split("-")
            data_smeta['date_smeta_num'] = date_smeta_num

            date_smeta = issue['fields']['created'][0:10].split("-")
            num_month(date_smeta)
            date_smeta_buckets = date_smeta.copy()
            date_smeta_buckets[2] = 'от "' + date_smeta_buckets[2] + '"'
            date_smeta_buckets[0] = date_smeta_buckets[0] + 'г.'
            date_smeta_buckets_string = date_smeta_buckets[2] + ' ' + date_smeta_buckets[1] + ' ' + date_smeta_buckets[0]
            data_smeta['date_smeta_buckets_string'] = date_smeta_buckets_string
            data_smeta['date_smeta_metrology'] = date_smeta
            date_smeta_num = issue['fields']['created'][0:10].split("-")
            data_smeta['date_smeta_num_metrology'] = date_smeta_num

        #---------------------

        # дата обновления заявки

        if 'updated' in issue['fields']:
            updated_smeta = issue['fields']['updated'][0:10].split("-")
            num_month(updated_smeta)
            data_smeta['updated'] = updated_smeta

            updated_num = issue['fields']['updated'][0:10].split("-")
            data_smeta['updated_num'] = updated_num

        #---------------------

        #Цель командировки----
        if 'customfield_14805' in issue['fields']:
            target_trip = issue['fields']['customfield_14805']  #Недолжно превышать 65 символов!!!!! ДОБАВИТЬ ОБРЕЗАТОР
            data_smeta['target_trip'] = target_trip
        #Руководитель подразделения, который подписывает бумагу
        if 'customfield_14828' in issue['fields'] and issue['fields']['customfield_14828'] != None:
            manager = issue['fields']['customfield_14828'].split(" ")

            data_smeta['manager'] = manager
        #---------------------
        if 'customfield_14826' in issue['fields'] and issue['fields']['customfield_14826'] != None:
            manager_new = issue['fields']['customfield_14826'].split("_pk_")

            data_smeta['manager_new'] = manager_new[0].split(' ')

            manager = issue['fields']['customfield_14826'].split(" ")

            data_smeta['manager_metrology'] = manager[0] + ' ' + manager[1] + ' ' + manager[2]

            data_smeta['manager_short'] = manager[0] + ' ' + manager[1][0] + '.' + manager[2][0] + '.'
        #---------------------
        #дата начала периода (переработка) дата и время
        if 'customfield_14824' in issue['fields'] and issue['fields']['customfield_14824'] != None:
            date_start = issue['fields']['customfield_14824'].split("T")
            date_start[0] = date_start[0].split('-')
            date_start[1] = date_start[1].split(':')
            data_smeta['date_start'] = date_start
        #---------------------
        #дата окончания периода (переработка)
        if 'customfield_14825' in issue['fields'] and issue['fields']['customfield_14825'] != None:
            date_end = issue['fields']['customfield_14825'].split("T")
            date_end[0] = date_end[0].split('-')
            date_end[1] = date_end[1].split(':')
            data_smeta['date_end'] = date_end
        #---------------------
        #место выполнения работ (переработка) ограничени 69 -70 символов
        if 'customfield_14823' in issue['fields']:
            position_working = issue['fields']['customfield_14823']  #.split(" ")
            tmp = dedent(position_working)
            tmp.strip()
            wrapper = TextWrapper(width=69)
            new_text = wrapper.fill(tmp)
            new_text = new_text.split('\n')
            data_smeta['position_working'] = new_text
        #---------------------
        #Сотрудники (multiple value)
        if 'customfield_14867' in issue['fields']:
            workers = issue['fields']['customfield_14867'].split("###")
            data_smeta['workers'] = workers
        #---------------------
        #Сотрудник (single value)(fullname сотрудника)
        if 'customfield_14822' in issue['fields'] and issue['fields']['customfield_14822'] != None:
            worker = issue['fields']['customfield_14822']
            if worker.find(' (') > 0:
                worker = worker.split(' (')
            else:
                worker = worker.split('_pk_')
            data_smeta['worker'] = worker[0]
        #---------------------
        #Должность
        if 'customfield_14911' in issue['fields']:
            position = issue['fields']['customfield_14911']
            data_smeta['position'] = position
        #---------------------
        # Пол сотрудника
        if 'customfield_14901' in issue['fields'] and issue['fields']['customfield_14901'] != None:
            sex_worker = issue['fields']['customfield_14901']['value']
            data_smeta['sex_worker'] = sex_worker
        #---------------------
        # Номер телефона
        if 'customfield_12708' in issue['fields'] and issue['fields']['customfield_12708'] != None:
            tel = issue['fields']['customfield_12708']
            data_smeta['tel'] = tel
            telnum = issue['fields']['customfield_12708']
            data_smeta['telnum'] = telnum
        else:
            data_smeta['tel'] = ''
        #---------------------
        # Вид отпуска
        if 'customfield_14914' in issue['fields'] and issue['fields']['customfield_14914'] != None:
            variety_leave = issue['fields']['customfield_14914']['value']
            data_smeta['variety_leave'] = variety_leave
        else:
            data_smeta['variety_leave'] = 'Не выбрано'
        #---------------------
        # дата начала
        if 'customfield_14919' in issue['fields'] and issue['fields']['customfield_14919'] != None:
            date_leave = issue['fields']['customfield_14919'].split('-')
            num_month(date_leave)
            data_smeta['date_leave'] = date_leave

            date_leave_num = issue['fields']['customfield_14919'].split('-')
            data_smeta['date_leave_num'] = date_leave_num

        #---------------------
        # кол-во дней
        if 'customfield_14920' in issue['fields'] and issue['fields']['customfield_14920'] != None:
            num_leave = issue['fields']['customfield_14920']
            data_smeta['num_leave'] = str(int(num_leave))
        #---------------------
        # компенсация отпуска да/нет
        if 'customfield_14922' in issue['fields'] and issue['fields']['customfield_14922'] != None:
            cash_leave = issue['fields']['customfield_14922']
            data_smeta['cash_leave'] = cash_leave
        #---------------------
        # Вид дополнительного отпуска отпуска
        if 'customfield_14916' in issue['fields'] and issue['fields']['customfield_14916'] != None:
            dop_leave = issue['fields']['customfield_14916']['value']
            data_smeta['dop_leave'] = dop_leave
        else:
            data_smeta['dop_leave'] = 'Не выбрано'
        #---------------------
        # дата справка-вызов дополнительного отпуска отпуска
        if 'customfield_14924' in issue['fields'] and issue['fields']['customfield_14924'] != None:
            ref_date_leave = issue['fields']['customfield_14924']
            data_smeta['ref_date_leave'] = ref_date_leave
        #---------------------
        # номер справка-вызов дополнительного отпуска отпуска
        if 'customfield_14923' in issue['fields'] and issue['fields']['customfield_14923'] != None:
            ref_num_leave = issue['fields']['customfield_14923']
            data_smeta['ref_num_leave'] = ref_num_leave
        #---------------------
        # начало периода работы отпуска отпуска
        if 'customfield_14928' in issue['fields'] and issue['fields']['customfield_14928'] != None:
            start_distance_leave = issue['fields']['customfield_14928'].split("-")
            data_smeta['start_distance_leave'] = start_distance_leave
        #эту лажу потом закоментить. это для отладки
        else:
            start_distance_leave = ''
            temp = start_distance_leave.split("-")
            # num_month(temp)
            data_smeta['start_distance_leave'] = temp

        #---------------------
        # окончание периода работы отпуска отпуска
        if 'customfield_14929' in issue['fields'] and issue['fields']['customfield_14929'] != None:
            # print('fdsfsdfsdfffffffffffffffffffffffffffffffffffffffffffffffffffffff')
            stop_distance_leave = issue['fields']['customfield_14929'].split("-")
            data_smeta['stop_distance_leave'] = stop_distance_leave
        #эту лажу потом закоментить. это для отладки
        else:
            stop_distance_leave = ''
            temp = stop_distance_leave.split("-")
            # num_month(temp)
            data_smeta['stop_distance_leave'] = temp
        #---------------------
        # остаток дней отпуска
        if 'customfield_14930' in issue['fields'] and issue['fields']['customfield_14930'] != None:
            balance_day_leave = issue['fields']['customfield_14930']
            data_smeta['balance_day_leave'] = str(int(balance_day_leave))
        #---------------------
        # список жалобщиков в акте об отсутствии на рабочем месте
        if 'customfield_16100' in issue['fields']:
            customstring = issue['fields']['customfield_16100']

            complainers = []
            complainerstemp = []
            complainer = {}
            key = [[] for j in range(0, customstring.count('], [') + 1)]
            value = [[] for j in range(0, customstring.count('], [') + 1)]

            customstring = customstring.replace('[[', '[')
            customstring = customstring.replace(']]', ']')

            for i in range(customstring.count('], [') + 1):
                stringindexitem = customstring.find("]")

                complainerstemp.append(customstring[1:stringindexitem])

                customstring = customstring.replace(customstring[1:stringindexitem], '')
                customstring = customstring.replace(customstring[0:4], '')

                keystaff = complainerstemp[i].find(':')

                keyposition = complainerstemp[i].rfind(':')

                keyseparator = complainerstemp[i].find(',')

                key[i].append(complainerstemp[i][0:keystaff])
                key[i].append(complainerstemp[i][keyseparator + 2:keyposition])

                value[i].append(complainerstemp[i][keystaff + 1:keyseparator])
                value[i].append(complainerstemp[i][keyposition + 1:])

                complainer = dict(zip(key[i], value[i]))
                complainers.append(complainer)

            data_smeta['complainers'] = complainers
        #---------------------
        #Название организации
        if 'customfield_14831' in issue['fields']:
            company = issue['fields']['customfield_14831']

            data_smeta['company2'] = company

            company = issue['fields']['customfield_14831']

            data_smeta['company_metrology'] = company
            #---------------------
        # Должность прогулявшего работу сотрудника
        if 'customfield_14847' in issue['fields']:
            position_absence = issue['fields']['customfield_14847']
            data_smeta['position_absence'] = position_absence
            #---------------------
        #дата отсутствия работника на рабочем месте. год-месяц-день
        if 'customfield_15602' in issue['fields'] and issue['fields']['customfield_15602'] != None:
            date_absence = []
            date_temp = issue['fields']['customfield_15602']
            date_absence.append(date_temp.split('-'))
            for i in range(len(date_absence[0])):
                date_absence[0][i] = date_absence[0][i]

            data_smeta['date_absence'] = date_absence  # date_end [['2022', '04', '04']]
            #---------------------
        #доступно дней
        if 'customfield_17306' in issue['fields']:
            available_days = issue['fields']['customfield_17306']
            # print('available_days-->', available_days)

            data_smeta['available_days'] = available_days
            #---------------------
        #вид увольнение
        if 'customfield_17308' in issue['fields'] and issue['fields']['customfield_17308'] != None:
            variety_dismissal = issue['fields']['customfield_17308']['value']
            data_smeta['variety_dismissal'] = variety_dismissal
        else:
            data_smeta['variety_dismissal'] = 'none'
            #--------------------------------
        #дата согласования сторон
        if 'customfield_14905' in issue['fields'] and issue['fields']['customfield_14905'] != None:
            date_dismissal = issue['fields']['customfield_14905']
            data_smeta['date_dismissal'] = date_dismissal
        else:
            data_smeta['date_dismissal'] = 'none'

        # данные о компании и сотруднике для переработок
        if 'customfield_16705' in issue['fields'] and issue['fields']['customfield_16705'] != None:
            # print(issue['fields']['customfield_16705'])
            # ========================= подключаем config =============================
            config = configparser.ConfigParser()  # создаём объекта парсера
            config.read(config_path)  # читаем конфиг arg['config_path']
            # =========================================================================
            #здесь указан путь к папке, где лежит jira_connect.py коннект к Жыре
            sys.path.append(config['scrypts_path']['path_jira'])
            import jira_connect
            # print('sdff')
            result = {}
            company_list = []
            worker_list = []
            manager_list = []
            # print(issue['fields']['customfield_16705'])
            for i in issue['fields']['customfield_16705']:
                # word = jira_connect.connect(argv[1], arg['Login'], arg['Password'])
                if i['fields']['issuetype']['name'] == 'Организация':
                    # print(config['jira']['rest']+'issue='+i['key']+'&fields=customfield_18200', login, password)

                    # запрос в карточку компании, что бы выяснить директора (ФИО, issuekey, статус)
                    dir_word_issue = jira_connect.connect(
                        config['jira']['rest'] + 'issue=' + i['key'] + '&fields=customfield_18200', login, password)

                    # print(config['jira']['rest']+'issue='+i['key']+'&fields=customfield_18200', login, password)

                    # запрос в карточку директора, что бы выяснить его подпись
                    dir_sig_word_issue = jira_connect.connect(config['jira']['rest'] + 'issue=' +
                                                              dir_word_issue['issue']['issues'][0]['fields'][
                                                                  'customfield_18200']['key'] + '&fields=customfield_18202',
                                                              login, password)

                    # запрос в карточку компании, что бы выяснить замдиректора (ФИО, issuekey, статус)
                    fixdir_word_issue = jira_connect.connect(
                        config['jira']['rest'] + 'issue=' + i['key'] + '&fields=customfield_18201', login, password)

                    # запрос в карточку замдиректора, что бы выяснить его подпись
                    fixdir_sig_word_issue = jira_connect.connect(config['jira']['rest'] + 'issue=' +
                                                                 fixdir_word_issue['issue']['issues'][0]['fields'][
                                                                     'customfield_18201'][
                                                                     'key'] + '&fields=customfield_18202', login, password)

                    company_list.append({'company_name': i['fields']['summary'],
                                         'company_key': i['key'],
                                         'director_name':
                                             dir_word_issue['issue']['issues'][0]['fields']['customfield_18200']['fields'][
                                                 'summary'],
                                         'director_status':
                                             dir_word_issue['issue']['issues'][0]['fields']['customfield_18200']['fields'][
                                                 'status']['name'],
                                         'director_position': 'Директор',
                                         'director_signature': dir_sig_word_issue['issue']['issues'][0]['fields'][
                                             'customfield_18202'],
                                         'fixdirector_name':
                                             fixdir_word_issue['issue']['issues'][0]['fields']['customfield_18201'][
                                                 'fields']['summary'],
                                         'fixdirector_status':
                                             fixdir_word_issue['issue']['issues'][0]['fields']['customfield_18201'][
                                                 'fields']['status']['name'],
                                         'fixdirector_position': 'Заместитель директора',
                                         'fixdirector_signature': fixdir_sig_word_issue['issue']['issues'][0]['fields'][
                                             'customfield_18202']
                                         })

                    # print(company_list)

                if i['fields']['issuetype']['name'] == 'Сотрудник':
                    # запрос в карточку сотрудника, что бы выяснить его подпись, имя, issuekey
                    word_issue = jira_connect.connect(
                        config['jira']['rest'] + 'issue=' + i['key'] + '&fields=customfield_18202', login, password)

                    # запрос для выяснения должности сотрудника
                    position_issue = jira_connect.connect(config['jira']['rest'] + 'parent=' + i[
                        'key'] + '%20and%20issuetype=Компания%20and%20status=Трудоустройство%20and%20cf[14866]=%22Основное%20место%20трудоустройства%22&fields=customfield_14847',
                                                          login, password)

                    split_position = position_issue['issue']['issues'][0]['fields']['customfield_14847'].split('_pk_')

                    worker_list.append({'worker_name': i['fields']['summary'],
                                        'worker_key': i['key'],
                                        'worker_position': split_position[0],
                                        'worker_signature': word_issue['issue']['issues'][0]['fields']['customfield_18202']
                                        })

            if 'customfield_14826' in issue['fields'] and issue['fields']['customfield_14826'] != None:

                manager_new = issue['fields']['customfield_14826'].split("_pk_")

                manager_signature = jira_connect.connect(
                    config['jira']['rest'] + 'project=DIRECTORY%20and%20issuetype=Сотрудник%20and%20cf[14822]=%22' +
                    manager_new[0].replace(' ', '%20') + '%22&fields=customfield_18202', login, password)
                manager_position = jira_connect.connect(config['jira'][
                                                            'rest'] + 'project=DIRECTORY%20and%20issuetype=Компания%20and%20status=Трудоустройство%20and%20cf[14866]=%22Основное%20место%20трудоустройства%22and%20cf[14822]=%22' +
                                                        manager_new[0].replace(' ', '%20') + '%22&fields=customfield_14847',
                                                        login, password)

                if manager_position['issue']['issues'][0]['fields']['customfield_14847'].find('_pk_'):
                    manager_position_pk = \
                        manager_position['issue']['issues'][0]['fields']['customfield_14847'].split('_pk_')[0]
                else:
                    manager_position_pk = manager_position['issue']['issues'][0]['fields']['customfield_14847']
                # manager_position_pk

                manager_list.append(
                    {'manager_signature': manager_signature['issue']['issues'][0]['fields']['customfield_18202'],
                     'manager_name': manager_new[0].replace(' ', '%20'),
                     'manager_position': manager_position_pk
                     })

                result['managers'] = manager_list

            result['company'] = company_list
            result['workers'] = worker_list

            # print(result)
            data_smeta['company-workers'] = result

        # настоящий директор компании (для переработок)
        if 'customfield_18200' in issue['fields'] and issue['fields']['customfield_18200'] != None:
            real_director_name = issue['fields']['customfield_18200']['fields']['summary']
            real_director_key = issue['fields']['customfield_18200']['key']

            data_smeta['real_director_name'] = real_director_name
            data_smeta['real_director_key'] = real_director_key

            # print('real_director_name-->>', real_director_name)
            # print('real_director_key-->>', real_director_key)
        else:
            data_smeta['real_director_name'] = 'none'
            data_smeta['real_director_key'] = 'none'

        # заместитель директор (для переработок)
        if 'customfield_18201' in issue['fields'] and issue['fields']['customfield_18201'] != None:
            fix_director_name = issue['fields']['customfield_18201']['fields']['summary']
            fix_director_key = issue['fields']['customfield_18201']['key']

            data_smeta['fix_director_name'] = fix_director_name
            data_smeta['fix_director_key'] = fix_director_key

            # print('fix_director_name-->>', fix_director_name)
            # print('fix_director_key-->>', fix_director_key)
        else:
            data_smeta['fix_director_name'] = 'none'
            data_smeta['fix_director_key'] = 'none'

        # производственный календарь
        if 'customfield_17901' in issue['fields']:
            work_calendar = issue['fields']['customfield_17901']
            # print('work_calendar-->', work_calendar)

            data_smeta['work_calendar'] = work_calendar
            #---------------------

        # способ компенсации за переработку
        # Предпочтительный вид компенсации
        if 'customfield_18203' in issue['fields'] and issue['fields']['customfield_18203'] != None:
            pay = issue['fields']['customfield_18203']['value']
            data_smeta['pay'] = pay

        # Номер приказа для новых переработок
        if 'customfield_14820' in issue['fields'] and issue['fields']['customfield_14820'] != None:
            owerwork_order = issue['fields']['customfield_14820'].split(',')
            data_smeta['owerwork_order'] = owerwork_order

        #владелец СИ
        if 'customfield_17802' in issue['fields']:
            owner = issue['fields']['customfield_17802']
            data_smeta['owner'] = owner
        #---------------------

        #ИНН владельца СИ
        if 'customfield_14115' in issue['fields']:
            owner_inn = issue['fields']['customfield_14115']
            data_smeta['owner_inn'] = str(int(owner_inn))
        #---------------------

        #наименование СИ
        if 'customfield_16703' in issue['fields']:
            nameSI = issue['fields']['customfield_16703']
            data_smeta['nameSI'] = nameSI['value']
        #---------------------

        #тип, модификация СИ
        if 'customfield_17206' in issue['fields']:
            typeSI = issue['fields']['customfield_17206']
            data_smeta['typeSI'] = typeSI['value']
        #---------------------

        #номер в госреестре СИ
        if 'customfield_17301' in issue['fields']:
            numSI = issue['fields']['customfield_17301']
            data_smeta['numSI'] = numSI
        #---------------------

        #заводской номер комплекса
        if 'customfield_13200' in issue['fields']:
            idSI = issue['fields']['customfield_13200']
            data_smeta['idSI'] = idSI
        #---------------------

        #дополнительные сведения
        if 'customfield_17805' in issue['fields']:
            dop = issue['fields']['customfield_17805']
            dopCell = ['–', '–', '–', '–']
            for i in dop:
                if i['value'] == 'Срочность': dopCell[0] = '+'
                if i['value'] == 'Протокол поверки': dopCell[1] = '+'
                if i['value'] == 'Свидетельство о поверке на бумаге': dopCell[2] = '+'
                if i['value'] == 'Опубликование сведений о владельце СИ во ФГИС': dopCell[3] = '+'
            data_smeta['dopCell'] = dopCell
        #---------------------

        #Примечание
        if 'description' in issue['fields']:
            # print(issue['fields'])
            description = issue['fields']['description']
            data_smeta['description'] = description

            # ---------------------------------
        # почта
        if 'customfield_12709' in issue['fields']:
            email = issue['fields']['customfield_12709']
            data_smeta['email'] = email

        #ИНН организации (Заказчика)
        if 'customfield_13000' in issue['fields']:
            inn = issue['fields']['customfield_13000']
            data_smeta['inn'] = str(int(inn))

            # категория поверки
        if 'customfield_17803' in issue['fields'] and issue['fields']['customfield_17803'] != None:
            verification = issue['fields']['customfield_17803'][0]['value']

            # print('verification', verification)
            if verification == 'Первичная':
                verification = 'на ПЕРВИЧНУЮ ПОВЕРКУ'

            data_smeta['verification'] = verification
        if 'customfield_17803' in issue['fields'] and issue['fields']['customfield_17803'] == None:
            verification = 'на ПОВЕРКУ'
            data_smeta['verification'] = verification
        # ----------------------------------------

        # категория поверки
        if 'customfield_17803' in issue['fields'] and issue['fields']['customfield_17803'] != None:
            verification = issue['fields']['customfield_17803'][0]['value']

            if verification == 'Первичная':
                verification = 'на ПЕРВИЧНУЮ ПОВЕРКУ'

            data_smeta['verification'] = verification
        if 'customfield_17803' in issue['fields'] and issue['fields']['customfield_17803'] == None:
            verification = 'на ПОВЕРКУ'
            data_smeta['verification'] = verification
        # ----------------------------------------
        # тема заявки
        if 'customfield_17804' in issue['fields']:
            topic = issue['fields']['customfield_17804'].split(":")
            data_smeta['topic'] = topic[0].replace('/', '_')
        #---------------------
        return data_smeta

        # дата обновления заявки
        # print('дата согласования-->> ', issue['fields']['updated'])
        # if 'created' in issue['fields']:
        #     updated_smeta = issue['fields']['updated'][0:10].split("-")
        #     num_month(updated_smeta)
        #     data_smeta['updated'] = updated_smeta

        #     updated_num = issue['fields']['updated'][0:10].split("-")
        #     data_smeta['updated_num'] = updated_num

        #---------------------
