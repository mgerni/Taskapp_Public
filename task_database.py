import random
import re
from math import floor
import tasklists
import config
import user_dao
from user_dao import UserDatabaseObject, convert_database_user
from user_migrate import migrate_database_user_to_new_format
from task_types import TaskData, LeaderboardEntry, TaskData

mydb = config.MONGO_CLIENT["TaskApp"]

# For old taskList data format
'''
get_user

Gets the UserDatabaseObject for a given username

Args:
    str: username

Returns:
    UserDatabaseObject

'''


def get_user(username) -> UserDatabaseObject:
    coll = mydb['taskAccounts']
    users = list(coll.find({'username': username}))
    if len(users) == 0:
        raise Exception("No user found with username " + username)
    old_user_data = users[0]
    return convert_database_user(migrate_database_user_to_new_format(old_user_data))


# For new taskList data format - Replaces above after migration
def get_user_2(username) -> UserDatabaseObject:
    coll = mydb['taskLists']
    users = list(coll.find({'username': username}))
    if len(users) == 0:
        raise Exception("No user found with username " + username)
    user_data = users[0]
    return convert_database_user(user_data)


'''
add_task_account:

The add_task_account function create document for the user in the taskAccounts collection.
The document is a dictionary with some of the keys being lists of dictionaries.
The document is structured as follows:
{
    _id : randomly generated id,
    username : username,
    isOfficial : True/False,
    lmsEnabled : True/False,
    easyTasks: [
        {
            _id : #,
            taskname : {
                name of the task : image matching the task, # would have done this differently since it horrible
                LMS : True/False
            },
            status: Incomplete/Complete,
            taskCurrent : True/False,
            taskTip : tip for the task,
            wikiLink : link to the wiki page for the task
        }
    ],
    mediumTasks: [ same as easyTasks ],
    hardTasks: [ same as easyTasks ],
    eliteTasks: [ same as easyTasks ]
    bossPetTasks: [ same as easyTasks except does not include taskTip ],
    otherPetTasks: [ same as easyTasks except does not include taskTip ],
    skillingPetTasks: [ same as easyTasks except does not include taskTip ],
    extraTasks: [ same as easyTasks except does not include taskTip ],
    passiveTasks: [ same as easyTasks except does not include taskTip ]
}

Args:
    str: username - username of the user.
    list: completions - list of tasks
    bool: isofficial - True/False
    bool: lmsenabled - True/False

Returns:
    None

'''


def add_task_account(username, isOfficial, lmsEnabled):
    coll = mydb['taskAccounts']

    def combine_tasks(tasks: list[TaskData]):
        new_tasks = []
        for task in tasks:
            new_tasks.append(
                {
                    "_id": task.id,
                    "taskname": {task.name: task.asset_image, 'LMS': task.is_lms},
                    "status": 'Incomplete',
                    "taskCurrent": False,
                    "taskTip": task.tip,
                    "wikiLink": task.wiki_link,
                    "taskImage": task.wiki_image
                }
            )
        return new_tasks

    taskAccount = {
        "username": str(username),
        "isOfficial": bool(isOfficial),
        "lmsEnabled": bool(lmsEnabled),
        "easyTasks": combine_tasks(tasklists.easy),
        "mediumTasks": combine_tasks(tasklists.medium),
        "hardTasks": combine_tasks(tasklists.hard),
        "eliteTasks": combine_tasks(tasklists.elite),
        "masterTasks": combine_tasks(tasklists.master),
        "bossPetTasks": combine_tasks(tasklists.boss_pet),
        "skillPetTasks": combine_tasks(tasklists.skill_pet),
        "otherPetTasks": combine_tasks(tasklists.other_pet),
        "extraTasks": combine_tasks(tasklists.extra),
        "passiveTasks": combine_tasks(tasklists.passive)
    }

    coll.insert_one(taskAccount)


'''
get_taskCurrent

The get_taskCurrent function, gets the current task for a user.
Used for official accounts.

Args:
    str: username - username of the user.

Returns:
    tuple: name of the task, image for the task, tier of the task, id of the task, tip for the task, wiki link for the task.

'''


def get_taskCurrent(username):
    return get_user(username).current_task()


'''
get_taskCurrent_tier

The get_taskCurrent_tier function, gets the current task for a user.
Used for unofficial accounts.

Args:
    str: username - username of the user.
    str: tier - tier of the task.

Returns:
    tuple: name of the task, image for the task, tier of the task, id of the task, tip for the task, wiki link for the task.

'''


def get_taskCurrent_tier(username, tier):
    return get_user(username).current_task_for_tier(tier)


def __set_current_task(username: str, tier: str, task_id: str, current: bool):
    coll = mydb['taskAccounts']
    coll.update_one({'username': username, '%s._id' % tier: task_id}, {'$set': {'%s.$.taskCurrent' % tier: current}})


def __set_task_complete(username: str, tier: str, task_id: int, complete: bool):
    coll = mydb['taskAccounts']
    coll.update_one({'username': username, '%s._id' % tier: task_id},
                    {'$set': {'%s.$.status' % tier: 'Complete' if complete else 'Incomplete',
                              '%s.$.taskCurrent' % tier: False}})


'''
generate_task_unofficial_tier:

The generate_task_unofficial_tier function, randomly generates a task for a unofficial user.
taskCurrent is set to True for the choosen task. 
Unofficial accounts are allowed to re-roll tasks. If they already have a task, the taskCurrent is set to False.


Args:
    str: username - username of the user.
    str: tier - tier of the task.

Returns:
    None

'''
def generate_task_for_tier(username, tier) ->TaskData or None: # type: ignore
    user = get_user(username)
    uncompleted_tasks = []

    if user.current_task_for_tier(tier) is None:
        all_tasks = tasklists.list_for_tier(tier, user.lms_enabled)
        completed_task_ids = list(map(lambda x: x.task_id, user.get_task_list(tier).completed_tasks))
        uncompleted_tasks = list(filter(lambda x: x.id not in completed_task_ids, all_tasks))

    if len(uncompleted_tasks) != 0:
        if tier == "masterTasks" and uncompleted_tasks[0].id == 1:
            generated_task = uncompleted_tasks[0]
            __set_current_task(username, tier, generated_task.id, True)
            return generated_task
        
        generated_task = random.choice(uncompleted_tasks)
        __set_current_task(username, tier, generated_task.id, True)
        return generated_task

    else:
        task_info = user.current_task_for_tier(tier)
        task_tier = task_info[2]
        task_number = task_info[3]
        __set_current_task(username, task_tier, task_number, False)
        return None

'''
generate_task:

The generate_task function, randomly generates a task for a official user.
lists of tasks are gathered for each tier. 
A task is choosen from the first tier that has tasks.
This allows for new tasks to be added in a lower tier due to game updates. 
taskCurrent is set to True for the choosen task. 

Args:
    str: username - username of the user.

Returns:
    TaskData: The generated task, or None if user already has a task

'''


def generate_task(username: str) -> TaskData or None: # type: ignore
    user = get_user(username)
    if user.current_task() is not None:
        return

    def get_incomplete_tasks(tier: str) -> list[TaskData]:
        all_tasks = tasklists.list_for_tier(tier, user.lms_enabled)
        completed_task_ids = list(map(lambda x: x.task_id, user.get_task_list(tier).completed_tasks))
        return list(filter(lambda x: x.id not in completed_task_ids, all_tasks))

    tasks_easy = get_incomplete_tasks('easy')
    tasks_medium = get_incomplete_tasks('medium')
    tasks_hard = get_incomplete_tasks('hard')
    tasks_elite = get_incomplete_tasks('elite')
    tasks_master = get_incomplete_tasks('master')

    if len(tasks_easy) != 0:
        generated_task = random.choice(tasks_easy)
        __set_current_task(username, 'easyTasks', generated_task.id, True)
        return generated_task
    elif len(tasks_medium) != 0:
        generated_task = random.choice(tasks_medium)
        __set_current_task(username, 'mediumTasks', generated_task.id, True)
        return generated_task
    elif len(tasks_hard) != 0:
        generated_task = random.choice(tasks_hard)
        __set_current_task(username, 'hardTasks', generated_task.id, True)
        return generated_task
    elif len(tasks_elite) != 0:
        generated_task = random.choice(tasks_elite)
        __set_current_task(username, 'eliteTasks', generated_task.id, True)
        return generated_task
    elif len(tasks_master) != 0:
        if tasks_master[0].id == 1:
            generated_task = tasks_master[0]
        else:
            generated_task = random.choice(tasks_master)
        __set_current_task(username, 'masterTasks', generated_task.id, True)
        return generated_task
    return None

# If user has just completed a task of the given tier and the progress is 100, then they've just completed the last task
def __get_firework_variables(username, tier):
    user = get_user(username)
    if user.get_tier_progress(tier) == 100:
        query_param_str = {
            'easyTasks': 'easy-first',
            'mediumTasks': 'medium-first',
            'hardTasks': 'hard-first',
            'eliteTasks': 'elite-first'
        }[tier]
        return {query_param_str: True}
    return {}


'''
complete_task_unofficial_tier:

The complete_task_unofficial_tier function, completes the current task for an unofficial user.
taskCurrent is set to False for the current task.
status is set to 'Complete' for the current task.

Functions also checks progress before and after for 100% completion.

Args:
    str: username - username of the user.
    str: tier - tier of the task.
    int: task_id - id of the task.

Returns:
    dict: Contains URL parameters specific for showing the fireworks when a tier goes from 99 -> 100% complete

'''


def complete_task_unofficial_tier(username: str, task_id: int, tier: str) -> dict:
    __set_task_complete(username, tier, task_id, True)
    return __get_firework_variables(username, tier)


'''
complete_task:

The complete_task function, completes the current task for an official user.
taskCurrent is set to False for the current task.
status is set to 'Complete' for the current task.

Functions also checks progress before and after for 100% completion.

Args:
    str: username - username of the user.
    str: tier - tier of the task.
    int: task_id - id of the task.

Returns:
    dict: Contains URL parameters specific for showing the fireworks when a tier goes from 99 -> 100% complete

'''


def complete_task(username: str) -> dict:
    user = get_user(username)
    task_check = user.current_task()

    if task_check is None:
        return {}

    tier = task_check[2]
    task_id = task_check[3]
    __set_task_complete(username, tier, task_id, True)

    return __get_firework_variables(username, tier)


'''
get_task_progress:

The get_task_progress function, determines the percentage of progress for each tier. Rounded down. 

Args:
    str: username - username of the user.


Returns:
    tuple: easy_progress, medium_progress, hard_progress, elite_progress - percentage of progress for each tier.

'''


def get_task_progress(username: str):
    user = get_user(username)
    easy = user.get_tier_progress('easy')
    medium = user.get_tier_progress('medium')
    hard = user.get_tier_progress('hard')
    elite = user.get_tier_progress('elite')
    master = user.get_tier_progress('master')
    passive = user.get_tier_progress('passive')
    extra = user.get_tier_progress('extra')
    boss_pets = user.get_tier_progress('bossPets')
    skill_pets = user.get_tier_progress('skillPets')
    other_pets = user.get_tier_progress('otherPets')
    all_pets_total = boss_pets.total + skill_pets.total + other_pets.total
    all_pets_total_complete = boss_pets.total_complete + skill_pets.total_complete + other_pets.total_complete
    all_pets_percent_complete = floor(all_pets_total_complete / all_pets_total * 100)

    progress = {
            'easy' : {'percent_complete' : easy.percent_complete, "total_complete" : easy.total_complete , "total" : easy.total},
            'medium' : {'percent_complete' : medium.percent_complete, "total_complete" : medium.total_complete , "total" : medium.total},
            'hard' : {'percent_complete' : hard.percent_complete, "total_complete" : hard.total_complete , "total" : hard.total},
            'elite' : {'percent_complete' : elite.percent_complete, "total_complete" : elite.total_complete , "total" : elite.total},
            'master' : {'percent_complete' : master.percent_complete, "total_complete" : master.total_complete , "total" : master.total},
            'passive' : {'percent_complete' : passive.percent_complete},
            'extra' : {'percent_complete' : extra.percent_complete},
            'all_pets' : {'percent_complete' : all_pets_percent_complete}
                }
    return progress
    return easy.percent_complete, medium.percent_complete, hard.percent_complete, elite.percent_complete, master.percent_complete, \
            passive.percent_complete, extra.percent_complete, all_pets_percent_complete, \
            easy.total_complete, easy.total, medium.total_complete, medium.total, hard.total_complete, hard.total, \
            elite.total_complete, elite.total, master.total_complete, master.total


'''
get_task_lists:

The get_task_lists function, generates the list of tasks for each tier.

# Can be optimized by doing a single query to the DB. 

Args:
    str: username - username of the user.


Returns:
    tuple: easy_list, medium_list, hard_list, elite_list bosspet_list, skillpet_list, otherpet_list, extra_list, passive_list - list of tasks for each tier.

'''


def get_task_lists(username):
    coll = mydb['taskAccounts']
    task_query_easy = coll.find({'username': username}, {'easyTasks': 1})
    task_query_medium = coll.find({'username': username}, {'mediumTasks': 1})
    task_query_hard = coll.find({'username': username}, {'hardTasks': 1})
    task_query_elite = coll.find({'username': username}, {'eliteTasks': 1})
    task_query_master = coll.find({'username': username}, {'masterTasks' : 1})
    task_query_bosspet = coll.find({'username': username}, {'bossPetTasks': 1})
    task_query_skillpet = coll.find({'username': username}, {'skillPetTasks': 1})
    task_query_otherpet = coll.find({'username': username}, {'otherPetTasks': 1})
    task_query_extra = coll.find({'username': username}, {'extraTasks': 1})
    task_query_passive = coll.find({'username': username}, {'passiveTasks': 1})

    easy_list = task_query_easy[0]['easyTasks']
    medium_list = task_query_medium[0]['mediumTasks']
    hard_list = task_query_hard[0]['hardTasks']
    elite_list = task_query_elite[0]['eliteTasks']
    master_list = task_query_master[0]['masterTasks']
    bosspet_list = task_query_bosspet[0]['bossPetTasks']
    skillpet_list = task_query_skillpet[0]['skillPetTasks']
    otherpet_list = task_query_otherpet[0]['otherPetTasks']
    extra_list = task_query_extra[0]['extraTasks']
    passive_list = task_query_passive[0]['passiveTasks']

    return easy_list, medium_list, hard_list, elite_list, master_list, bosspet_list, skillpet_list, otherpet_list, extra_list, passive_list


'''
manual_complete_tasks:

The manual_complete_tasks function, sets the status of a task to complete.

Args:
    str: username - username of the user.


Returns:
    tuple: name of the task, image of the task, tip of the task, link to the task.

'''


def manual_complete_tasks(username, tier, task_id):
    task_id = int(task_id)
    __set_task_complete(username, tier, task_id, True)
    exclude_list = ['bossPetTasks', 'skillPetTasks', 'otherPetTasks']
    if tier in exclude_list:
        tier = tier.replace('Tasks', 's')
    task = user_dao.task_info_for_id(tasklists.list_for_tier(tier), task_id)
    return task.name, task.asset_image, task.tip, task.wiki_link


'''
manual_revert_tasks:

The manual_revert_tasks function, sets the status of a task to Incomplete.

Args:
    str: username - username of the user.


Returns:
    tuple: name of the task, image of the task, tip of the task, link to the task.

'''


def manual_revert_tasks(username, tier, task_id):
    task_id = int(task_id)
    __set_task_complete(username, tier, task_id, False)
    exclude_list = ['bossPetTasks', 'skillPetTasks', 'otherPetTasks']
    if tier in exclude_list:
        tier = tier.replace('Tasks', 's')
    task = user_dao.task_info_for_id(tasklists.list_for_tier(tier), task_id)
    return task.name, task.asset_image, task.tip, task.wiki_link


'''
DEPRECATED - No replacement
import_spreadsheet:

The import_spreadsheet function, Imports a spreadsheet into the database.
Reads google sheets and imports it into the database.
A tier is only imported if the spreadsheet tasks length matches our task length. 
So that tasks are not updated with the wrong ID's. 

Args:
    str: username - username of the user.
    str: url - url of the spreadsheet.


# very annoying to maintain since it is a google sheet, order of their rows is important. 

Returns:
    str: error - error message if there is an error.
    list: each element is a str: of the tier import status. 

'''
# def import_spreadsheet(username, url):
#     def update_current_task_from_sheet(username, tier, task_id):
#         coll = mydb['taskAccounts']
#         task_check = coll.find_one({'username': username, '%s._id' % tier: task_id},
#                                    {'_id': 0, '%s.status' % tier: 1, '%s._id' % tier: 1})
#         task_updated = False
#         if task_check[tier][task_id - 1]['status'] == 'Incomplete':
#             task_updated = True
#             coll.update_one({'username': username, '%s._id' % tier: task_id},
#                             {'$set': {'%s.$.taskCurrent' % tier: True}})
#         return task_updated

#     try:
#         error = None
#         task_import_logs = []
#         task_current_logs = []
#         speadsheet_key = re.search('\/d\/(.*?)(\/|$)', url)
#         if speadsheet_key:
#             service = gspread.service_account(filename="service_account.json")
#             google_sheet = service.open_by_key(speadsheet_key.group(1))
#             info_sheet = google_sheet.worksheet("Info")

#             current_sheet_tier = info_sheet.get('B13:B14')

#             tier, cell = current_sheet_tier[0][0], current_sheet_tier[1][0].replace('C', "")
#             cell = int(cell) - 1
#             sheet_tasks = []
#             sheet_list = [
#                 'Easy',
#                 'Medium',
#                 'Hard',
#                 'Elite',
#                 'Pets',
#                 'Pets',
#                 'Pets',
#                 'Extra',
#                 'Passive'
#             ]

#             cell_range = [
#                 'A2:C137',  # Easy
#                 'A2:C160',  # Medium
#                 'A2:C184',  # Hard
#                 'A2:C165',  # Elite
#                 'A2:C35',  # Pets - Boss
#                 'A37:C44',  # Pets - Skill
#                 'A46:C55',  # Pets - Other
#                 'A2:C119',  # Extra
#                 'A2:C44'  # Passive
#             ]

#             task_list = [
#                 tasklists.easy,
#                 tasklists.medium,
#                 tasklists.hard,
#                 tasklists.elite,
#                 tasklists.boss_pet,
#                 tasklists.skill_pet,
#                 tasklists.other_pet,
#                 tasklists.extra,
#                 tasklists.passive
#             ]

#             taskdb_names = [
#                 'easyTasks',
#                 'mediumTasks',
#                 'hardTasks',
#                 'eliteTasks',
#                 'bossPetTasks',
#                 'skillPetTasks',
#                 'otherPetTasks',
#                 'extraTasks',
#                 'passiveTasks'
#             ]

#             for sheet_name, cells in zip(sheet_list, cell_range):
#                 ws = google_sheet.worksheet(sheet_name)
#                 tasks = ws.get(cells)
#                 sheet_tasks.append(tasks)
#                 if sheet_name == tier:
#                     current_list = []
#                     current_list.append(tasks)

#             coll = mydb['taskAccounts']
#             user_tasks = coll.find_one({'username': username})

#             for sheet_task_list, tasks_lists, doc_list_names in zip(sheet_tasks, task_list, taskdb_names):
#                 if len(sheet_task_list) == len(tasks_lists):
#                     for i, (task_sheet, task_db) in enumerate(zip(sheet_task_list, tasks_lists), 1):
#                         if 'x' in task_sheet:
#                             user_tasks[doc_list_names][i - 1]['status'] = "Complete"
#                     coll.update_one({'username': username}, {'$set': {doc_list_names: user_tasks[doc_list_names]}})
#                     task_import_logs.append('Tasks for %s were updated!' % doc_list_names)
#                 else:
#                     task_import_logs.append(
#                         'Unable to update %s! Spreadsheet data differs from database!' % doc_list_names)

#             if get_taskCurrent(username) is None:
#                 for i, (task) in enumerate(current_list[0], 1):
#                     if i == cell:
#                         sheets_db_dict = {}
#                         for i2, (key, value) in enumerate(zip(sheet_list, taskdb_names)):
#                             sheets_db_dict[key] = value
#                             if i2 == 3:
#                                 update_current = update_current_task_from_sheet(username, sheets_db_dict[tier], i)
#                                 if update_current is True:
#                                     task_current_logs.append('Updated current task!')
#                                     break
#             else:
#                 task_current_logs.append('Current task already found!')
#         else:
#             error = "Spreadsheet URL is not valid!"
#         return task_import_logs, task_current_logs, error
#     except Exception as e:
#         print(str(e))
#         error = "There was a problem prcoessing the request. Contact Gerni Task on Discord."
#         return task_import_logs, task_current_logs, error


# NOT USED only for testing purposes.
def uncomplete_all_tasks(username):
    task_list = ['easyTasks', 'mediumTasks', 'hardTasks', 'eliteTasks']
    coll = mydb['taskAccounts']
    user_info = coll.find({'username': username})
    for info in user_info:
        for tier in task_list:
            task_tier = tier
            for task in info[tier]:
                if task['status'] == "Complete":
                    task_id = task['_id']
                    coll.update_one({'username': username, '%s._id' % tier: task_id},
                                    {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier: 'Incomplete'}})
    task_check = get_taskCurrent(username)
    if task_check is not None:
        tier = task_check[2]
        task_id = task_check[3]
        coll.update_one({'username': username, '%s._id' % tier: task_id},
                        {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier: 'Incomplete'}})


'''
lms_status_change:

The lms_status_change function, sets lmsEnabled to true or false for a given user.


Args:
    str: username - The username of the user to change the lms status for.
    bool: lmsEnabled - Whether the user is lms enabled or not.

Returns:
        None

'''


def lms_status_change(username, lms_status):
    coll = mydb['taskAccounts']
    coll.update_one({'username': username}, {'$set': {'lmsEnabled': lms_status}})


'''
official_status_change:

The official_status_change function, sets officialEnabled to true or false for a given user.


Args:
    str: username - The username of the user to change the lms status for.
    
Returns:
        None

'''


def official_status_change(username):
    coll = mydb['taskAccounts']
    coll.update_one({'username': username}, {'$set': {'isOfficial': False}})


'''
username_change:

The username_change function, changes the username of a user.


Args:
    str: username - The username of the user.
    str: username_value - The new username of the user.
    
Returns:
        str: error - The error message if there is one.
        bool: success - Whether the username change was successful or not.

'''


def username_change(username, username_value):
    coll = mydb['taskAccounts']
    doc_count_new_username = coll.count_documents({'username': username_value})
    if doc_count_new_username != 0:
        error = 'Username already exists'
        return error
    else:
        coll.update_one({'username': username}, {'$set': {'username': username_value}})
        success = True
        return success


'''
official_icon:

The official_icon function, determines the icon to display for official users.

Args:
    int: easy - easy percentage
    int: medium - medium percentage
    int: hard - hard percentage
    int: elite - elite percentage

Returns:
       str: rank_icon - The icon to display.

'''


def official_icon(easy, medium, hard, elite):
    if elite >= 50 and hard == 100 and medium == 100 and easy == 100:
        rank_icon = '/static/assets/rank_icons/Zenyte.png'

    elif elite <= 49 and hard == 100 and medium == 100 and easy == 100:
        rank_icon = '/static/assets/rank_icons/Onyx.png'

    elif hard >= 50 and medium == 100 and easy == 100:
        rank_icon = '/static/assets/rank_icons/Diamond.png'

    elif hard <= 49 and medium == 100 and easy == 100:
        rank_icon = '/static/assets/rank_icons/Ruby.png'

    elif medium >= 50 and easy == 100:
        rank_icon = '/static/assets/rank_icons/Emerald.png'

    elif medium <= 49 and easy == 100:
        rank_icon = '/static/assets/rank_icons/Sapphire.png'

    elif easy >= 50:
        rank_icon = '/static/assets/rank_icons/RedTopaz.png'

    elif easy <= 49:
        rank_icon = '/static/assets/rank_icons/Minion.png'

    return rank_icon


'''
unoffical_log_count:

The unoffical_log_count function, gives a rough collection log count for an unofficial user.

# Since tasks are not 1:1 to collection log slots, many tasks have increases to their log count. 

Args:
    str: username - The username of the user.
    
Returns:
       str: total_count - The total log count for the user.

'''


def unoffical_log_count(username):
    coll = mydb['taskAccounts']
    easy_completed = 0
    medium_completed = 0
    hard_completed = 0
    elite_completed = 0
    pet_completed = 0
    extra_completed = 0
    passive_completed = 0
    dragon_hat_count = 0
    champscroll_count = 0
    unsired_count = 0
    grace_count = 0
    agility_ticket_count = 0
    task_query = coll.find({'username': username},
                           {
                               'easyTasks': 1,
                               'mediumTasks': 1,
                               'hardTasks': 1,
                               'eliteTasks': 1,
                               'extraTasks': 1,
                               'bossPetTasks': 1,
                               'skillPetTasks': 1,
                               'otherPetTasks': 1,
                               'passiveTasks': 1
                           })

    for task in task_query:
        for ele in task['easyTasks']:
            if ele['status'] == 'Complete':
                easy_completed += 1
                for key in ele['taskname']:
                    if key == 'Get 3 new uniques from beginner clues':
                        easy_completed += 2
                    if key == 'Get 5 new uniques from easy clues':
                        easy_completed += 4
                    if key == 'Get 5 new uniques from medium clues':
                        easy_completed += 4
                    if key == 'Get 5 new uniques from hard clues':
                        easy_completed += 4
                    if key == 'Get 2 unique notes from Fossil Island':
                        easy_completed += 1
                    if key == 'Get 2 unique Ancient pages':
                        easy_completed += 1
                    if key == 'Get the Marksman headpiece':
                        easy_completed += 5
                    if key == 'Get a Rune defender':
                        easy_completed += 6
                    if key == 'Get the full Red decorative set':
                        easy_completed += 7
                    if key == 'Get the Zamorak hood & cloak':
                        easy_completed += 1
                    if key == 'Get the Saradomin hood & cloak':
                        easy_completed += 1
                    if key == 'Get a Mole claw + skin':
                        easy_completed += 1
                    if key == 'Get a Fresh crab claw & Fresh crab shell':
                        easy_completed += 1
                    if key == 'Get 5 unique items at Camdozaal':
                        easy_completed += 4
                    if key == 'Get 1 piece of Graceful equipment':
                        if grace_count != 1:
                            easy_completed += 1
                            grace_count += 1

                    if key == 'Complete the Ardougne Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Desert Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Falador Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Fremennik Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Kandarin Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Karamja Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Kourend&Kebos Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Lumbridge&Draynor Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Morytania Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Varrock Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Western Provinces Easy Diary':
                        easy_completed -= 1
                    if key == 'Complete the Wilderness Easy Diary':
                        easy_completed -= 1

                    if key == 'Get 1 unique Champion scroll':
                        champscroll_count += 1

        for ele in task['mediumTasks']:
            if ele['status'] == 'Complete':
                medium_completed += 1
                for key in ele['taskname']:
                    if key == 'Get 3 new uniques from beginner clues':
                        medium_completed += 2
                    if key == 'Get 5 new uniques from easy clues':
                        medium_completed += 4
                    if key == 'Get 5 new uniques from medium clues':
                        medium_completed += 4
                    if key == 'Get 5 new uniques from hard clues':
                        medium_completed += 4
                    if key == 'Get 2 unique notes from Fossil Island':
                        medium_completed += 1
                    if key == 'Get 2 unique Ancient pages':
                        medium_completed += 1
                    if key == 'Get the Ogre forester headpiece':
                        medium_completed += 2
                    if key == 'Get 1 Naval set':
                        medium_completed += 2
                    if key == 'Get tier 5 Shayzien armour':
                        medium_completed += 24
                    if key == 'Get the Decorative ranged set':
                        medium_completed += 2
                    if key == 'Get the Decorative magic set':
                        medium_completed += 2

                    if key == 'Complete the Ardougne Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Desert Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Falador Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Fremennik Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Kandarin Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Karamja Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Kourend&Kebos Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Lumbridge&Draynor Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Morytania Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Varrock Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Western Provinces Medium Diary':
                        medium_completed -= 1
                    if key == 'Complete the Wilderness Medium Diary':
                        medium_completed -= 1

                    if key == 'Get 1 unique Champion scroll':
                        champscroll_count += 1

        for ele in task['hardTasks']:
            if ele['status'] == 'Complete':
                hard_completed += 1
                for key in ele['taskname']:
                    if key == 'Get 3 new uniques from beginner clues':
                        hard_completed += 2
                    if key == 'Get 5 new uniques from easy clues':
                        hard_completed += 4
                    if key == 'Get 5 new uniques from medium clues':
                        hard_completed += 4
                    if key == 'Get 5 new uniques from hard clues':
                        hard_completed += 4
                    if key == 'Get 2 new uniques from elite clues':
                        hard_completed += 1
                    if key == 'Get 2 unique Ancient pages':
                        hard_completed += 1
                    if key == 'Get 2 uniques from the Hallowed Sepulchre':
                        hard_completed += 1
                    if key == 'Unlock 2 monkey backpack transformations':
                        hard_completed += 1
                    if key == 'Get the Ogre expert headpiece':
                        hard_completed += 3
                    if key == 'Get 1 Naval set':
                        hard_completed += 2
                    if key == 'Get a new Boss pet':
                        hard_completed -= 1
                    if key == 'Get 2 White decorative pieces':
                        hard_completed += 1

                    if key == 'Complete the Ardougne Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Desert Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Falador Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Fremennik Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Kandarin Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Karamja Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Kourend&Kebos Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Lumbridge&Draynor Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Morytania Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Varrock Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Western Provinces Hard Diary':
                        hard_completed -= 1
                    if key == 'Complete the Wilderness Hard Diary':
                        hard_completed -= 1
                    if key == 'Get 1 unique Champion scroll':
                        champscroll_count += 1
                    if key == 'Get a unique from Unsired':
                        if unsired_count != 1:
                            hard_completed += 1
                            unsired_count += 1
                    if key == 'Get the Brimhaven graceful set recolour' or "Get a Pirate's hook":
                        if agility_ticket_count != 1:
                            hard_completed += 1
                            agility_ticket_count += 1

        for ele in task['eliteTasks']:
            if ele['status'] == 'Complete':
                elite_completed += 1
                for key in ele['taskname']:
                    if key == 'Upgrade to the (expert) dragon archer headpiece':
                        if dragon_hat_count != 1:
                            elite_completed += 2
                            dragon_hat_count += 1
                        else:
                            elite_completed += 1
                    if key == 'Get 5 new uniques from easy clues':
                        elite_completed += 4
                    if key == 'Get 5 new uniques from medium clues':
                        elite_completed += 4
                    if key == 'Get 5 new uniques from hard clues':
                        elite_completed += 4
                    if key == 'Get 2 unique Ancient pages':
                        elite_completed += 1
                    if key == 'Get 1 Naval set':
                        elite_completed += 2
                    if key == 'Get the Chompy chick':
                        elite_completed -= 1

                    if key == 'Complete the Ardougne Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Desert Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Falador Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Fremennik Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Kandarin Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Karamja Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Kourend&Kebos Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Lumbridge&Draynor Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Morytania Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Varrock Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Western Provinces Elite Diary':
                        elite_completed -= 1
                    if key == 'Complete the Wilderness Elite Diary':
                        elite_completed -= 1

                    if key == 'Get 1 unique Champion scroll':
                        champscroll_count += 1
                        if champscroll_count == 10:
                            elite_completed += 1

        for ele in task['extraTasks']:
            if ele['status'] == 'Complete':
                extra_completed += 1
                for key in ele['taskname']:
                    if key == 'Finish all easy clue uniques':
                        extra_completed += 20
                    if key == 'Finish all medium clue uniques':
                        extra_completed += 24
                    if key == 'Finish all hard clue uniques':
                        extra_completed += 28
                    if key == 'Finish all elite clue uniques':
                        extra_completed += 28
                    if key == 'Finish all master clue uniques':
                        extra_completed += 37
                    if key == 'Finish all shared clue rewards ':
                        extra_completed += 48
                    if key == 'Finish all hard clue rare uniques':
                        extra_completed += 23
                    if key == 'Finish all elite clue rare uniques':
                        extra_completed += 14
                    if key == 'Finish all master rare clue uniques':
                        extra_completed += 5
                    if key == 'Complete the Gold decorative set':
                        extra_completed += 3

        for ele in task['bossPetTasks']:
            if ele['status'] == 'Complete':
                pet_completed += 1

        for ele in task['skillPetTasks']:
            if ele['status'] == 'Complete':
                pet_completed += 1

        for ele in task['otherPetTasks']:
            if ele['status'] == 'Complete':
                pet_completed += 1

        for ele in task['passiveTasks']:
            if ele['status'] == 'Complete':

                passive_completed += 1
                for key in ele['taskname']:
                    if key == 'Get all random event outfits':
                        passive_completed += 22

    total_count = easy_completed + medium_completed + hard_completed + floor(
        elite_completed) + pet_completed + extra_completed + passive_completed
    return total_count


'''
unofficial_icon:

The unofficial_icon function, determines the rank_icon to be displayed for unofficial users. 

# TODO: add recently added rank_icon

Args:
    str: username - The username of the user.
    
Returns:
       str: rank_icon - The rank_icon to be displayed.

'''


def unofficial_icon(username):
    log_count = unoffical_log_count(username)
    if log_count >= 1000:
        rank_icon = '/static/assets/rank_icons/Elite.png'
    elif log_count >= 750:
        rank_icon = '/static/assets/rank_icons/Completionist.png'
    elif log_count >= 500:
        rank_icon = '/static/assets/rank_icons/Achiever.png'
    elif log_count >= 250:
        rank_icon = '/static/assets/rank_icons/Explorer.png'
    else:
        rank_icon = '/static/assets/rank_icons/Minion.png'

    return rank_icon

def get_leaderboard() -> list[LeaderboardEntry]:
    def to_user(data):
        user = convert_database_user(migrate_database_user_to_new_format(data))
        return LeaderboardEntry(user.username, user.lms_enabled, user.get_tier_progress('easy'),
                                user.get_tier_progress('medium'), user.get_tier_progress('hard'),
                                user.get_tier_progress('elite'), user.get_tier_progress('master'))

    coll = mydb['taskAccounts']
    return list(sorted(map(to_user, coll.find({'isOfficial': True})), key=lambda x: x.points(), reverse=True))


if __name__ == "__main__":
    pass
