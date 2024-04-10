import config

'''
The methods in this file are for migrating users data from the old format to the new format
They are to be removed
'''

mydb = config.MONGO_CLIENT["TaskApp"]

def migrate_user_tier_list(tier_list):
    filtered_completed_tier_list = filter(lambda x: x['status'] == 'Complete', tier_list)
    converted_completed_tier_list = list(map(lambda x: {'taskId': x['_id']}, filtered_completed_tier_list))
    filtered_completed_tier_list = list(filter(lambda x: x['taskCurrent'], tier_list))
    new_tier_list_object = {}
    if len(filtered_completed_tier_list) > 0:
        new_tier_list_object['currentTask'] = {
            'taskId': filtered_completed_tier_list[0]['_id']
        }
    new_tier_list_object['completedTasks'] = converted_completed_tier_list
    return new_tier_list_object

def migrate_database_user_to_new_format(user: dict) -> dict:
    return {
        '_id': user['_id'],
        'username': user['username'],
        'isOfficial': user['isOfficial'],
        'lmsEnabled': user['lmsEnabled'],
        'tiers': {
            'easy': migrate_user_tier_list(user['easyTasks']),
            'medium': migrate_user_tier_list(user['mediumTasks']),
            'hard': migrate_user_tier_list(user['hardTasks']),
            'elite': migrate_user_tier_list(user['eliteTasks']),
            'passive': migrate_user_tier_list(user['passiveTasks']),
            'extra': migrate_user_tier_list(user['extraTasks']),
            'bossPets': migrate_user_tier_list(user['bossPetTasks']),
            'skillPets': migrate_user_tier_list(user['skillPetTasks']),
            'otherPets': migrate_user_tier_list(user['otherPetTasks'])
        }
    }

'''
migrate_db:

Migrates all users to new format in a new table called taskLists
'''
def migrate_db():
    coll = mydb['taskAccounts']
    new_coll = mydb['taskLists']  # Can't seem to find a way to easily rewrite to existing collection
    new_coll.drop()
    users = coll.find({}, {})

    for user in users:
        new_coll.insert_one(migrate_database_user_to_new_format(user))


# Below to replace task_database.py add user
'''
add_task_account:

The add_task_account function creates the document for the user in the taskLists collection.
The document is structured as follows:
{
    _id : randomly generated id user id,
    username: '',
    isOfficial: true/false,
    lmsEnabled: false/false,
    tiers: {
        easyTier: {
            currentTask: {
                "taskId": Matches the ids in task JSONs,
                "assignedDate": "some date/time format"
            },
            completedTasks: [ # only stores completed tasks
                {
                    "taskId": "Maybe a new id field here that matches new field in task list jsons?",
                    "completionDate": "some date/time format", # both dates are nullable
                    "assignedDate": "some date/time format from above assignedDate field"
                },...
            ],
        }
        medium: {same as easyTier},
        hard: {same as easyTier},
        elite: {same as easyTier},
        passive: {same as easyTier},
        extra: {same as easyTier},
        bossPets: {same as easyTier},
        skillPets: {same as easyTier},
        otherPets: {same as easyTier}
    }
}

Args:
    str: username - username of the user.
    bool: is_official - True/False
    bool: lms_enabled - True/False

Returns:
    None

'''
def add_task_account(username, is_official, lms_enabled):
    coll = mydb['taskLists']
    coll.insert_one({
        "username": str(username),
        "isOfficial": bool(is_official),
        "lmsEnabled": bool(lms_enabled),
        'tiers': {
            'easy': [],
            'medium': [],
            'hard': [],
            'elite': [],
            'passive': [],
            'extra': [],
            'bossPets': [],
            'skillPets': [],
            'otherPets': []
        }
    })
