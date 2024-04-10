import requests
import json
from tasklists import TaskData

def get_collection_log(rsn):
    rsn = rsn.replace(' ', '%20')
    response = requests.get("https://api.collectionlog.net/collectionlog/user/%s" % rsn)
    response_info = json.loads(response.text)

    return response.status_code, response_info

def check_collection_log(task_list: list[TaskData], log_data):
    missing_tasks = []
    valid = True
    debug = False

    if debug:
        log_data['collectionLog']['tabs']['Bosses']['Barrows Chests']['items'][24]['obtained'] = False
        log_data['collectionLog']['tabs']['Bosses']['Giant Mole']['items'][1]['obtained'] = False
        log_data['collectionLog']['tabs']['Bosses']['Wintertodt']['items'][1]['obtained'] = False
        log_data['collectionLog']['tabs']['Bosses']['Tempoross']['items'][4]['obtained'] = False
        log_data['collectionLog']['tabs']['Other']['Slayer']['items'][0]['obtained'] = False

    for i, task in enumerate(task_list, 1):
        if task.col_log_data is None:
            continue

        taskname = task.name
        category = task.col_log_data.category
        logname = task.col_log_data.log_name
        include_list = task.col_log_data.include
        exclude_list = task.col_log_data.exclude
        db_count = task.col_log_data.log_count  # Expected number of logs for a given task
        log_count = 0  # Current count of that log in collection log data

        # print(log_data)
        items = log_data['collectionLog']['tabs'][category][logname]['items']

        if include_list:
            for item in items:
                if item['name'] in include_list:
                    if item['obtained']:
                        log_count += 1

                    if db_count == log_count:
                        break

            if db_count != log_count:
                valid = False
                missing_tasks.append(taskname)
            print('[%s]: Proccessed Task: [%s:%s] in %s. Counts: [DB: %s] [LOG: %s]' %(i, taskname, item['name'], logname, db_count, log_count))

        if exclude_list:
            for item in items:
                if item['name'] not in exclude_list:
                    if item['obtained']:
                        log_count += 1

                    if db_count == log_count:
                        break

            if db_count != log_count:
                valid = False
                missing_tasks.append(taskname)
            print('[%s]: Proccessed Task: [%s:%s] in %s. Counts: [DB: %s] [LOG: %s]' %(i, taskname, item['name'], logname, db_count, log_count))
    return valid, missing_tasks

if __name__ == '__main__':
    pass
