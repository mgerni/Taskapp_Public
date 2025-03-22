import requests
import json


def temple_player_data(username: str):
    username = username.replace(' ', '+')
    player_data = requests.get(f'https://templeosrs.com/api/collection-log/player_collection_log.php?player={username}&categories=all&itemsonly&includenames=1&onlyitems=1').json()
    return player_data


def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def test():
    data = temple_player_data('Gerni Task')
    for item in data['data']['items']:
        print(item['name'])

def check_logs(username: str, site_tasks: list):
    player_data = temple_player_data(username)
    missing_tasks = list()
    for task in site_tasks:
        task_data = task.get('colLogData', None)
        if task_data:
            log_count = 0
            for item in task_data['include']:
                for log_slot in player_data['data']['items']:
                    if item['id'] == log_slot['id']:
                        log_count += 1
                    if log_count == task_data['logCount']:
                        break
            if log_count != task_data['logCount']:
                missing_tasks.append(task['name'])
    return missing_tasks