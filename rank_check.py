import requests
import json

def get_collection_log(rsn):
    rsn = rsn.replace(' ', '%20')
    response = requests.get("https://api.collectionlog.net/collectionlog/user/%s" % rsn)
    response_info = json.loads(response.text)

    return response.status_code, response_info

def check_collection_log(task_list, log_data):
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
        taskname = task['taskName']
        category = task['category']
        logname = task['logName']
        items = log_data['collectionLog']['tabs'][category][logname]['items']
        
        if task.get('include'):
            for item in items:
                if item['name'] in task['include']:
                    if item['obtained'] == True:
                        task['log_count'] += 1

                    if task['db_count'] == task['log_count']:
                        break
            
            if task['db_count'] != task['log_count']:
                valid = False
                missing_tasks.append(taskname)
            print('[%s]: Proccessed Task: [%s:%s] in %s. Counts: [DB: %s] [LOG: %s]' %(i, taskname, item['name'], logname, task['db_count'], task['log_count']))

        if task.get('exclude'):
            for item in items:
                if item['name'] not in task['exclude']:
                    if item['obtained'] == True:
                        task['log_count'] += 1

                    if task['db_count'] == task['log_count']:
                        break
            
            if task['db_count'] != task['log_count']:
                valid = False
                missing_tasks.append(taskname)
            print('[%s]: Proccessed Task: [%s:%s] in %s. Counts: [DB: %s] [LOG: %s]' %(i, taskname, item['name'], logname, task['db_count'], task['log_count']))      
    return valid, missing_tasks

if __name__ == '__main__':
    pass
