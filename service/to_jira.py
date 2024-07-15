# Стандартные библиотеки
import os
# Сторонние библиотеки
from jira import JIRA
from config import settings


class Jira:
    issuekey = settings.ISSUE_KEY
    login = settings.ZABBIX_USER
    password = settings.ZABBIX_PASSWORD
    jira_server = settings.JIRA_SERVER

    @classmethod
    def attach(cls, year):
        file_name = f'{settings.DOC_PATH}{settings.DOC_NAME} {str(year)}{settings.DOC_TYPE}'
        jira_options = {'server': cls.jira_server}
        jira = JIRA(options=jira_options, basic_auth=(cls.login, cls.password))
        jql = "issuekey = \"" + cls.issuekey + "\" AND attachments is not EMPTY"
        query = jira.search_issues(jql_str=jql, json_result=True, fields="key, attachment")
        for i in query['issues']:
            for a in i['fields']['attachment']:
                if a['filename'].find('.xlsx') > 0:
                    try:
                        jira.delete_attachment(a['id'])
                    except Exception:
                        pass
        issue_j = jira.issue(cls.issuekey)
        jira.add_attachment(issue=issue_j, attachment=file_name)
