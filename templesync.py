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

    return cleaned_player_data


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
    def find_by_id(items, target_id):
        print(type(target_id))
        
        return [item for item in items if int(item['id']) == target_id]
    def format_completed_tasks(completed_tasks: set):
        # iterate over the completed tasks and create a list of dictionaries
        formatted_tasks = []
        for task_id in completed_tasks:
            formatted_tasks.append({
                'taskId': task_id,
            })
        return formatted_tasks

    cleaned_player_data = temple_player_data(username)
    print(type(cleaned_player_data))
    missing_tasks = list()
    completed_tasks = set()
    for task in site_tasks:
        task_data = task.get('colLogData', None)
        if task_data:
            log_count = 0
            for item in task_data['include']:
                print(f"Checking item: {item['name']} with ID: {item['id']}")
                find_item = find_by_id(cleaned_player_data, item['id'])
                if find_item:
                    log_count += 1
                    print(f"Found item: {find_item[0]['name']} with ID: {find_item[0]['id']}")
                    print(f"Log count: {log_count}, Required: {task_data['logCount']}")
                    if log_count == task_data['logCount']:
                        completed_tasks.add(int(task['_id']))
                        print(f"Completed task: {task['name']} with ID: {task['_id']}")
                        break
            if log_count != task_data['logCount']:
                missing_tasks.append(task['name'])
                print(f"Missing task: {task['name']} with ID: {task['_id']}")
                    
    if action == 'check':
        print("Missing tasks:")
        for task in missing_tasks:
            print(task)
        return missing_tasks
    else:
        sorted_completed_tasks = sorted(completed_tasks)
        print(sorted_completed_tasks)
        return format_completed_tasks(sorted_completed_tasks)