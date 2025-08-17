import config

'''
The methods in this file are for migrating users data from the old format to the new format
They are to be removed
'''

mydb = config.MONGO_CLIENT["TaskApp"]

def migrate_task_list(tier_list: dict):
    if ('currentTask' in tier_list):
        tier_list['currentTask'] = { 'id': tier_list['currentTask']['uuid'] }

    tier_list['completedTasks'] = [{ 'id': task['uuid'] } for task in tier_list['completedTasks']]
    return tier_list

def merge_task_lists(tier_lists: list[dict]):
    new_tier_list_object = {}
    # this dark magic somehow flattens a list
    new_tier_list_object['completedTasks'] = [task for tier_list in tier_lists for task in tier_list['completedTasks']]
    return new_tier_list_object

def migrate_database_task_list_to_new_format(user: dict) -> dict:
    return {
        '_id': user['_id'],
        'username': user['username'],
        'isOfficial': user['isOfficial'],
        'lmsEnabled': user['lmsEnabled'],
        'tiers': {
            'easy': migrate_task_list(user['tiers']['easy']),
            'medium': migrate_task_list(user['tiers']['medium']),
            'hard': migrate_task_list(user['tiers']['hard']),
            'elite': migrate_task_list(user['tiers']['elite']),
            'master' : migrate_task_list(user['tiers']['master']),
            'passive': migrate_task_list(user['tiers']['passive']),
            'extra': migrate_task_list(user['tiers']['extra']),
            'pets': merge_task_lists([
                migrate_task_list(user['tiers']['bossPets']),
                migrate_task_list(user['tiers']['skillPets']),
                migrate_task_list(user['tiers']['otherPets']),
            ]),
        }
    }

'''
migrate_db:

Migrates all users to new format
'''
def migrate_db():
    coll = mydb['taskLists']
    task_lists = coll.find({}, {})

    for task_list in task_lists:
        coll.replace_one(
            { 'username': task_list['username'] },
            migrate_database_task_list_to_new_format(task_list),
        )

if __name__ == "__main__":
    migrate_db()