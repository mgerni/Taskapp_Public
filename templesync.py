import requests
import tasklists
from task_types import CollectionLogVerificationData, TaskData


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

# def test():
#     data = temple_player_data('Gerni Task')
#     for item in data['data']['items']:
#         print(item['name'])

# def get_unix_time(timestamp: str):
#     datetime_format = "%Y-%m-%d %H:%M:%S"
#     datetime_object = datetime.datetime.strptime(timestamp, datetime_format)
#     return time.mktime(datetime_object.timetuple())

# def import_logs(player_name: str, site_tasks: list):
#     player_data = temple_player_data(player_name)
#     completed_tasks = list()
#     for task in site_tasks:
#         task_data = task.get('colLogData', None)
#         if task_data:
#             for item in task_data['include']:
#                 for log_slot in player_data['data']['items']:
#                     if item['id'] == log_slot['id']:
#                         completed_tasks.append(task['_id'])
#                         break
#     return completed_tasks


def check_logs(username: str, site_tasks: list["TaskData"], action: str):
    def find_by_id(items, target_id):
        return [item for item in items if int(item['id']) == target_id]
    def format_completed_tasks(completed_tasks: set):
        formatted_tasks = []
        for task_id in completed_tasks:
            formatted_tasks.append({
                'id' : task_id
            })
        return formatted_tasks

    cleaned_player_data = temple_player_data(username)
    missing_tasks = list()
    completed_tasks = set()
    for task in site_tasks:
        verification_data = task.verification
        if not isinstance(verification_data, CollectionLogVerificationData):
            print("Skipping")
            continue

        log_count = 0
        for itemId in verification_data.item_ids:
            # print(f"Checking item: {item['name']} with ID: {item['id']}")
            find_item = find_by_id(cleaned_player_data, itemId)
            if find_item:
                log_count += 1

        if log_count >= verification_data.count:
            completed_tasks.add(task.id)
        else:
            missing_tasks.append(task.name)

    if action == 'check':
        return missing_tasks
    else:
        sorted_completed_tasks = sorted(completed_tasks)
        # print(sorted_completed_tasks)
        return format_completed_tasks(sorted_completed_tasks)


if __name__ == "__main__":
    check_logs('Gerni Task', tasklists.list_for_tier('easy'), 'import')