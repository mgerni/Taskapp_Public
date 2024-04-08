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
# def add_task_account(username, is_official, lms_enabled):
#     coll = mydb['taskLists']
#     coll.insert_one({
#         "username": str(username),
#         "isOfficial": bool(is_official),
#         "lmsEnabled": bool(lms_enabled),
#         'tiers': {
#             'easy': [],
#             'medium': [],
#             'hard': [],
#             'elite': [],
#             'passive': [],
#             'extra': [],
#             'bossPets': [],
#             'skillPets': [],
#             'otherPets': []
#         }
