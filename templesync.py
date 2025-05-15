import requests
import json


def temple_player_data(username: str):
    username = username.replace(' ', '+')
    player_data = requests.get(f'https://templeosrs.com/api/collection-log/player_collection_log.php?player={username}&categories=all&itemsonly&includenames=1&onlyitems=1').json()
    used_id = set()
    cleaned_player_data = list()
    for item in player_data['data']['items']:
        if item['id'] not in used_id:
            used_id.add(item['id'])
            cleaned_player_data.append(item)

    return player_data


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def test():
    data = temple_player_data('Gerni Task')
    for item in data['data']['items']:
        print(item['name'])

def import_logs(player_name: str, site_tasks: list):
    player_data = temple_player_data(player_name)
    completed_tasks = list()
    for task in site_tasks:
        task_data = task.get('colLogData', None)
        if task_data:
            for item in task_data['include']:
                for log_slot in player_data['data']['items']:
                    if item['id'] == log_slot['id']:
                        completed_tasks.append(task['_id'])
                        break
    return completed_tasks


def check_logs(username: str, site_tasks: list, action: str):
    def format_completed_tasks(completed_tasks: set):
        # iterate over the completed tasks and create a list of dictionaries
        formatted_tasks = []
        for task_id in completed_tasks:
            formatted_tasks.append({
                'taskId': task_id,
            })
        return formatted_tasks

    player_data = temple_player_data(username)
    missing_tasks = list()
    completed_tasks = set()
    for task in site_tasks:
        task_data = task.get('colLogData', None)
        if task_data:
            log_count = 0
            for item in task_data['include']:
                for log_slot in player_data['data']['items']:
                    if item['id'] == log_slot['id']:
                        log_count += 1
                    if log_count == task_data['logCount']:
                        completed_tasks.add(int(task['_id']))
                        break
                if log_count != task_data['logCount']:
                    missing_tasks.append(task['name'])


    if action == 'check':
        return missing_tasks
    else:
        
        return format_completed_tasks(completed_tasks)