# Стандартные библиотеки
import os
# Сторонние библиотеки
from jira import JIRA
from config import Settings


class Jira:

    @classmethod
    def attach(cls, year, server):
        settings = Settings(_env_file=f'{server}.env')

        file_name = f'{settings.DOC_PATH}{settings.DOC_NAME} {str(year)}{settings.DOC_TYPE}'
        jira_options = {'server': settings.JIRA_SERVER}
        jira = JIRA(options=jira_options, basic_auth=(settings.ZABBIX_USER, settings.ZABBIX_PASSWORD))
        jql = "issuekey = \"" + settings.ISSUE_KEY + "\" AND attachments is not EMPTY"
        query = jira.search_issues(jql_str=jql, json_result=True, fields="key, attachment")
        for i in query['issues']:
            for a in i['fields']['attachment']:
                if a['filename'].find('.xlsx') > 0:
                    try:
                        jira.delete_attachment(a['id'])
                    except Exception:
                        pass
        issue_j = jira.issue(settings.ISSUE_KEY)
        jira.add_attachment(issue=issue_j, attachment=file_name)
