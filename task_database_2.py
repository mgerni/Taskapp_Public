import random
import gspread
import re
from math import floor
import tasklists
import config
from dataclasses import dataclass
from datetime import datetime
from bson.objectid import ObjectId

def task_info_for_id(task_list, task_id) -> tasklists.Task:
    filtered = list(filter(lambda x: x.id == task_id, task_list))
    if len(filtered) == 0:
        raise Exception("No id found in list " + task_id)
    return filtered[0]

def task_list_for_tier_string(tier) -> list[tasklists.Task]
    return {
        'easyTasks': tasklists.easy,
        'mediumTasks': tasklists.medium,
        'hardTasks': tasklists.hard,
        'eliteTasks': tasklists.elite,
        'easy': tasklists.easy,
        'medium': tasklists.medium,
        'hard': tasklists.hard,
        'elite': tasklists.elite
    }[tier]


@dataclass
class DatabaseCurrentTask:
    task_id: int
    assigned_date: datetime = None

@dataclass
class DatabaseCompletedTask:
    task_id: int
    assigned_date: datetime  = None
    completed_date: datetime = None

@dataclass
class UserTaskList:
    current_task: DatabaseCurrentTask
    completed_tasks: list[DatabaseCompletedTask]

@dataclass
class UserDatabaseObject:
    id: ObjectId
    username: str
    is_official: bool
    lms_enabled: bool
    easy: UserTaskList
    medium: UserTaskList
    hard: UserTaskList
    elite: UserTaskList
    passive: UserTaskList
    extra: UserTaskList
    boss_pets: UserTaskList
    skill_pets: UserTaskList
    other_pets: UserTaskList

    def get_task_list(self, tier: str) -> UserTaskList:
        return {
            'easyTasks': self.easy,
            'mediumTasks': self.medium,
            'hardTasks': self.hard,
            'eliteTasks': self.elite
        }[tier]

    def current_task_for_tier(self, tier: str) -> tuple or None:
        user_task_list = self.get_task_list(tier)
        if user_task_list.current_task is None:
            return None
        task = task_info_for_id(task_list_for_tier_string(tier), user_task_list.c)
        return task.name, task.asset_image, tier, task.id, task.tip, task.wiki_link, task.wiki_image

    def current_task(self):
        if self.easy.current_task is not None:
            task = task_info_for_id(tasklists.easy, self.easy.current_task.task_id)
            tier = 'easyTasks'
        elif self.medium.current_task is not None:
            task = task_info_for_id(tasklists.medium, self.medium.current_task.task_id)
            tier = 'mediumTasks'
        elif self.hard.current_task is not None:
            task = task_info_for_id(tasklists.hard, self.hard.current_task.task_id)
            tier = 'hardTasks'
        elif self.elite.current_task is not None:
            task = task_info_for_id(tasklists.hard, self.elite.current_task.task_id)
            tier = 'eliteTasks'
        else:
            return None
        return task.name, task.asset_image, tier, task.id, task.tip, task.wiki_link, task.wiki_image


mydb = config.MONGO_CLIENT["TaskApp"]


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

def database_tier(data: dict) -> UserTaskList:
    completed_tasks = list(map(lambda x: DatabaseCompletedTask(task_id= x['taskId']), data['completedTasks']))
    current = data.get('currentTask')
    if current:
        current = DatabaseCurrentTask(task_id=current['taskId'])
    return UserTaskList(current_task=current,
                        completed_tasks=completed_tasks)

def get_user(username) -> UserDatabaseObject:
    coll = mydb['taskLists']
    users = list(coll.find({'username': username}))
    if len(users) == 0:
        raise Exception("No user found with username " + username)
    user_data = users[0]
    tiers = user_data['tiers']
    return UserDatabaseObject(
        id=user_data['_id'],
        username=user_data['username'],
        is_official=user_data['isOfficial'],
        lms_enabled=user_data['lmsEnabled'],
        easy=database_tier(tiers['easy']),
        medium=database_tier(tiers['medium']),
        hard=database_tier(tiers['hard']),
        elite=database_tier(tiers['elite']),
        passive=database_tier(tiers['passive']),
        extra=database_tier(tiers['extra']),
        boss_pets=database_tier(tiers['bossPets']),
        skill_pets=database_tier(tiers['skillPets']),
        other_pets=database_tier(tiers['otherPets'])
    )


'''
get_taskCurrent

The get_taskCurrent function, gets the current task for a user.
Used for official accounts.

Args:
    str: username - username of the user.

Returns:
    tuple: name of the task, image for the task, tier of the task, id of the task, tip for the task, wiki link for the task.
    TODO Change to return a class
    TODO if we move these sorts of getter functions into the UserDatabaseObject class, then we reduce number of calls to Mongo 

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


'''
lms_check:

The lms_check function, checks if user has lms enabled.


Args:
    str: username - username of the user.

Returns:
    bool: True if lms is enabled, False if not.

'''
def lms_check(username):
    return get_user(username).lms_enabled


'''
official_check:

The official_check function, checks if user is official.


Args:
    str: username - username of the user.

Returns:
    bool: True if official, False if not.

'''
def official_check(username):
    return get_user(username).is_official

def __filtered_uncompleted_list(user_completed_tasks, tier, lms_enabled):
    user_completed_task_ids = list(map(lambda x: x.id, user_completed_tasks))
    task_list = task_list_for_tier_string(tier)
    uncompleted_tasks = list(filter(lambda x: x.id in user_completed_task_ids, task_list))

    if not lms_enabled:
        uncompleted_tasks = list(filter(lambda x: not x.is_lms, task_list))
    return uncompleted_tasks

def __set_current_task(username, tier, task_id):
    coll = mydb['taskLists']
    coll.update_one({'username': username}, {'$set' : {'%s.tiers.currentTask' % tier: {'taskId': task_id, 'assignedDate': datetime.now()}}})

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
def generate_task_unofficial_tier(username, tier):
    user = get_user(username)

    if user.current_task_for_tier(tier) is not None:
        # User already has a task
        return

    uncompleted_tasks = __filtered_uncompleted_list(user.get_task_list(tier), tier, user.lms_enabled)

    if len(uncompleted_tasks) != 0:
        generated_task = random.choice(uncompleted_tasks)
        __set_current_task(username, tier, generated_task.id)
    # else:
    #     task_info = get_taskCurrent_tier(username, tier)
    #     task_tier = task_info[2]
    #     task_number = task_info[3]
    #     coll.update_one({'username': username, '%s._id' % task_tier : task_number}, {'$set' : {'%s.$.taskCurrent' % tier: False }})


'''
generate_task:

The generate_task function, randomly generates a task for a official user.
lists of tasks are gathered for each tier. 
A task is choosen from the first tier that has tasks.
This allows for new tasks to be added in a lower tier due to game updates. 
taskCurrent is set to True for the choosen task. 


# This could be optimized by using a single DB query such as coll.find({'username': username}, {'easyTasks': 1, 'mediumTasks': 1, 'hardTasks': 1, 'eliteTasks': 1})
# Further optimized by not appending LMS tasks in the inital for loop. 


Args:
    str: username - username of the user.

Returns:
    None

'''
def generate_task(username):

    user = get_user(username)
    if user.current_task() is not None:
        # User already has a task
        return

    easy_tasks = __filtered_uncompleted_list(user.get_task_list('easy'), 'easy', user.lms_enabled)
    medium_tasks = __filtered_uncompleted_list(user.get_task_list('medium'), 'medium', user.lms_enabled)
    hard_tasks = __filtered_uncompleted_list(user.get_task_list('hard'), 'hard', user.lms_enabled)
    elite_tasks = __filtered_uncompleted_list(user.get_task_list('elite'), 'elite', user.lms_enabled)

    if len(easy_tasks) != 0:
        generated_task = random.choice(easy_tasks)
        __set_current_task(username, 'easy', generated_task.id)

    elif len(medium_tasks) != 0:
        generated_task = random.choice(medium_tasks)
        __set_current_task(username, 'medium', generated_task.id)

    elif len(hard_tasks) != 0:
        generated_task = random.choice(hard_tasks)
        __set_current_task(username, 'hard', generated_task.id)

    elif len(elite_tasks) != 0:
        generated_task = random.choice(elite_tasks)
        __set_current_task(username, 'elite', generated_task.id)





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
    None

'''
def complete_task_unofficial_tier(username, task_id, tier):
    coll = mydb['taskAccounts']
    progress_before = get_task_progress(username)
    coll.update_one({'username': username , '%s._id' % tier : task_id}, {'$set' : {'%s.$.status' % tier: 'Complete', '%s.$.taskCurrent' % tier: False }})


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
    None

'''
def complete_task(username):
    coll = mydb['taskAccounts']
    task_check = get_taskCurrent(username)
    progress_before = get_task_progress(username)
    easy_before, medium_before, hard_before, elite_before = progress_before[0], progress_before[1], progress_before[2], progress_before[3]

    if task_check is not None:
        tier = task_check[2]
        task_id = task_check[3]
        coll.update_one({'username' : username, '%s._id' % tier : task_id}, {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier : 'Complete'}})
        progress_after = get_task_progress(username)
        easy_after, medium_after, hard_after, elite_after = progress_after[0], progress_after[1], progress_after[2], progress_after[3]

    if easy_before != 100 and easy_after == 100:
        easy_first = True
        coll.update_one({'username': username}, {'$set' : {"easyFirst" : easy_first}})


    elif medium_before != 100 and medium_after == 100:
        medium_first = True
        coll.update_one({'username': username}, {'$set' : {"mediumFirst" : medium_first}})


    elif hard_before != 100 and hard_after == 100:
        hard_first = True
        coll.update_one({'username': username}, {'$set' : {"hardFirst" : hard_first}})


    elif elite_before != 100 and elite_after == 100:
        elite_first = True
        coll.update_one({'username': username}, {'$set' : {"eliteFirst" : elite_first}})



'''
get_tier_status:

The get_tier_status function, gets the tierFirst status of each tier.

Args:
    str: username - username of the user.


Returns:
    tuple: easy_first, medium_first, hard_first, elite_first - boolean values for each tier.

'''
def get_tier_status(username):
    coll = mydb['taskAccounts']
    x = coll.find_one({'username': username}, {'_id': 0, 'easyFirst': 1, 'mediumFirst': 1, 'hardFirst': 1, 'eliteFirst': 1})
    coll.update_one({'username': username}, {'$set': {'easyFirst': False, 'mediumFirst': False, 'hardFirst': False, 'eliteFirst' : False}})
    return x['easyFirst'], x['mediumFirst'], x['hardFirst'], x['eliteFirst']



'''
get_task_progress:

The get_task_progress function, determines the percentage of progress for each tier. Rounded down. 

Args:
    str: username - username of the user.


Returns:
    tuple: easy_progress, medium_progress, hard_progress, elite_progress - percentage of progress for each tier.

'''
def get_task_progress(username):

    tasks_easy = []
    tasks_medium = []
    tasks_hard = []
    tasks_elite = []
    easy_completed = 0
    medium_completed = 0
    hard_completed = 0
    elite_completed = 0

    coll = mydb['taskAccounts']

    task_query_easy = coll.find({'username': username}, {'easyTasks': 1})

    task_query_medium = coll.find({'username': username}, {'mediumTasks': 1})

    task_query_hard = coll.find({'username': username}, {'hardTasks': 1})

    task_query_elite = coll.find({'username': username}, {'eliteTasks': 1})


    lms_status = lms_check(username)

    for task in task_query_easy:
        for ele in task['easyTasks']:
            tasks_easy.append(ele)
            if lms_status is False:
                if ele['taskname']['LMS'] is True:
                    tasks_easy.remove(ele)
                    if ele['status'] == 'Complete':
                        easy_completed -= 1
            if ele['status'] == 'Complete':
                easy_completed += 1
    for task in task_query_medium:
        for ele in task['mediumTasks']:
            tasks_medium.append(ele)
            if lms_status is False:
                if ele['taskname']['LMS'] is True:
                    tasks_medium.remove(ele)
                    if ele['status'] == 'Complete':
                        medium_completed -= 1
            if ele['status'] == 'Complete':
                medium_completed += 1

    for task in task_query_hard:
        for ele in task['hardTasks']:
            tasks_hard.append(ele)
            if lms_status is False:

                if ele['taskname']['LMS'] is True:
                    tasks_hard.remove(ele)
                    if ele['status'] == 'Complete':
                        hard_completed -= 1
            if ele['status'] == 'Complete':
                hard_completed += 1

    for task in task_query_elite:
        for ele in task['eliteTasks']:
            tasks_elite.append(ele)
            if lms_status is False:
                if ele['taskname']['LMS'] is True:
                    tasks_elite.remove(ele)
                    if ele['status'] == 'Complete':
                        elite_completed -= 1
            if ele['status'] == 'Complete':
                elite_completed += 1

    total_easy = len(tasks_easy)
    total_medium = len(tasks_medium)
    total_hard = len(tasks_hard)
    total_elite = len(tasks_elite)

    percent_easy = floor(easy_completed / total_easy * 100)
    percent_medium = floor(medium_completed / total_medium * 100)
    percent_hard = floor(hard_completed / total_hard * 100)
    percent_elite = floor(elite_completed / total_elite * 100)


    return percent_easy, percent_medium, percent_hard, percent_elite, easy_completed, total_easy, medium_completed,total_medium,hard_completed, total_hard, elite_completed, total_elite



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
    task_query_bosspet = coll.find({'username': username}, {'bossPetTasks': 1})
    task_query_skillpet = coll.find({'username': username}, {'skillPetTasks': 1})
    task_query_otherpet = coll.find({'username': username}, {'otherPetTasks': 1})
    task_query_extra = coll.find({'username': username}, {'extraTasks': 1})
    task_query_passive = coll.find({'username': username}, {'passiveTasks': 1})

    easy_list = task_query_easy[0]['easyTasks']
    medium_list = task_query_medium[0]['mediumTasks']
    hard_list = task_query_hard[0]['hardTasks']
    elite_list = task_query_elite[0]['eliteTasks']
    bosspet_list = task_query_bosspet[0]['bossPetTasks']
    skillpet_list = task_query_skillpet[0]['skillPetTasks']
    otherpet_list = task_query_otherpet[0]['otherPetTasks']
    extra_list = task_query_extra[0]['extraTasks']
    passive_list = task_query_passive[0]['passiveTasks']

    return easy_list, medium_list, hard_list, elite_list, bosspet_list, skillpet_list, otherpet_list, extra_list, passive_list


'''
manual_complete_tasks:

The manual_complete_tasks function, sets the status of a task to complete.

Args:
    str: username - username of the user.


Returns:
    tuple: name of the task, image of the task, tip of the task, link to the task.

'''
def manual_complete_tasks(username, tier, task_id):
    coll = mydb['taskAccounts']
    exlude_tip = {'bossPetTasks', 'otherPetTasks', 'skillPetTasks', 'extraTasks', 'passiveTasks'}
    task_id = int(task_id)
    coll.update_one({'username' : username, '%s._id' % tier : task_id}, {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier : 'Complete'}})
    task_updated = coll.find({'username' : username, '%s._id' % tier : task_id}, {tier : 1, '_id': 0})
    for tasks in task_updated:
        for key, value in tasks.items():
            for task_dict in value:
                if task_id == task_dict['_id']:
                    link = task_dict['wikiLink']
                    if tier in exlude_tip:
                        tip = 'None'
                    else:
                        tip = task_dict['taskTip']
                    for task_name in task_dict['taskname'].items():
                        task = task_name[0]
                        image = task_name[1]
                        break

    return task, image, tip, link


'''
manual_revert_tasks:

The manual_revert_tasks function, sets the status of a task to Incomplete.

Args:
    str: username - username of the user.


Returns:
    tuple: name of the task, image of the task, tip of the task, link to the task.

'''
def manual_revert_tasks(username, tier, task_id):
    coll = mydb['taskAccounts']
    exlude_tip = {'bossPetTasks', 'otherPetTasks', 'skillPetTasks', 'extraTasks', 'passiveTasks'}
    task_id = int(task_id)
    coll.update_one({'username' : username, '%s._id' % tier : task_id}, {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier : 'Incomplete'}})
    task_revert = coll.find({'username' : username, '%s._id' % tier : task_id}, {tier : 1, '_id': 0})
    for tasks in task_revert:
        for key, value in tasks.items():
            for task_dict in value:
                if task_id == task_dict['_id']:
                    link = task_dict['wikiLink']
                    if tier in exlude_tip:
                        tip = 'None'
                    else:
                        tip = task_dict['taskTip']
                    for task_name in task_dict['taskname'].items():
                        task = task_name[0]
                        image = task_name[1]
                        break

    return task, image, tip, link




'''
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
def import_spreadsheet(username, url):
    def update_current_task_from_sheet(username, tier, task_id):
        coll = mydb['taskAccounts']
        task_check = coll.find_one({'username': username, '%s._id' % tier : task_id}, {'_id': 0, '%s.status' % tier : 1, '%s._id' % tier : 1})
        task_updated = False
        if task_check[tier][task_id - 1]['status'] == 'Incomplete':
            task_updated = True
            coll.update_one({'username' : username, '%s._id' % tier : task_id}, {'$set': {'%s.$.taskCurrent' % tier: True}})
        return task_updated
    try:
        error = None
        task_import_logs = []
        task_current_logs = []
        speadsheet_key = re.search('\/d\/(.*?)(\/|$)', url)
        if speadsheet_key:
            service = gspread.service_account(filename="service_account.json")
            google_sheet = service.open_by_key(speadsheet_key.group(1))
            info_sheet = google_sheet.worksheet("Info")

            current_sheet_tier = info_sheet.get('B13:B14')

            tier, cell = current_sheet_tier[0][0], current_sheet_tier[1][0].replace('C', "")
            cell = int(cell) - 1
            sheet_tasks = []
            sheet_list = [
                'Easy',
                'Medium',
                'Hard',
                'Elite',
                'Pets',
                'Pets',
                'Pets',
                'Extra',
                'Passive'
            ]

            cell_range = [
                'A2:C137', # Easy
                'A2:C160', # Medium
                'A2:C184',# Hard
                'A2:C165',# Elite
                'A2:C35', # Pets - Boss
                'A37:C44',# Pets - Skill
                'A46:C55', # Pets - Other
                'A2:C119', # Extra
                'A2:C44' # Passive
            ]


            task_list = [
                tasklists.easy,
                tasklists.medium,
                tasklists.hard,
                tasklists.elite,
                tasklists.boss_pet,
                tasklists.skill_pet,
                tasklists.other_pet,
                tasklists.extra,
                tasklists.passive
            ]

            taskdb_names = [
                'easyTasks',
                'mediumTasks',
                'hardTasks',
                'eliteTasks',
                'bossPetTasks',
                'skillPetTasks',
                'otherPetTasks',
                'extraTasks',
                'passiveTasks'
            ]



            for sheet_name, cells in zip(sheet_list,cell_range):
                ws = google_sheet.worksheet(sheet_name)
                tasks = ws.get(cells)
                sheet_tasks.append(tasks)
                if sheet_name == tier:
                    current_list = []
                    current_list.append(tasks)

            coll = mydb['taskAccounts']
            user_tasks = coll.find_one({'username': username})

            for sheet_task_list, tasks_lists, doc_list_names in zip(sheet_tasks, task_list, taskdb_names):
                if len(sheet_task_list) == len(tasks_lists):
                    for i, (task_sheet, task_db) in enumerate(zip(sheet_task_list, tasks_lists), 1):
                        if 'x' in task_sheet:
                            user_tasks[doc_list_names][i -1]['status'] = "Complete"
                    coll.update_one({'username': username}, {'$set': {doc_list_names : user_tasks[doc_list_names]}})
                    task_import_logs.append('Tasks for %s were updated!' % doc_list_names)
                else:
                    print(len(sheet_task_list), len(tasks_lists))
                    task_import_logs.append('Unable to update %s! Spreadsheet data differs from database!' % doc_list_names)

            if get_taskCurrent(username) is None:
                for i, (task) in enumerate(current_list[0], 1):
                    if i == cell:
                        sheets_db_dict = {}
                        for i2, (key, value) in enumerate(zip(sheet_list, taskdb_names)):
                            sheets_db_dict[key] = value
                            if i2 == 3:
                                update_current = update_current_task_from_sheet(username, sheets_db_dict[tier], i)
                                if update_current is True:
                                    task_current_logs.append('Updated current task!')
                                    break
            else:
                task_current_logs.append('Current task already found!')
        else:
            error = "Spreadsheet URL is not valid!"
        return task_import_logs, task_current_logs, error
    except Exception as e:
        print(str(e))
        error = "There was a problem prcoessing the request. Contact Gerni Task on Discord."
        return task_import_logs, task_current_logs, error


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
    coll = mydb['taskLists']
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
    coll = mydb['taskLists']
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
    coll = mydb['taskLists']
    success, error = False, None
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

    elif  hard <=49 and medium == 100 and easy == 100:
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
                'easyTasks' : 1,
                'mediumTasks' : 1,
                'hardTasks' : 1,
                'eliteTasks' : 1,
                'extraTasks' : 1,
                'bossPetTasks' : 1,
                'skillPetTasks' : 1,
                'otherPetTasks' : 1,
                'passiveTasks' : 1
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
                    if key =='Get a unique from Unsired':
                        if unsired_count != 1:
                            hard_completed += 1
                            unsired_count += 1
                    if key == 'Get the Brimhaven graceful set recolour' or "Get a Pirate's hook":
                        if agility_ticket_count != 1:
                            hard_completed += 1
                            agility_ticket_count +=1



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


    total_count = easy_completed + medium_completed + hard_completed + floor(elite_completed) + pet_completed + extra_completed +passive_completed
    # print('Easy: %s, Medium: %s, Hard: %s , Elite: %s, Pet: %s: Extra: %s, Passive: %s. TOTAL: %s' % (easy_completed , medium_completed , hard_completed , floor(elite_completed) , pet_completed , extra_completed ,passive_completed, total_count))
    # print(total_count)
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


def convert_user_tier_list(tier_list):
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

def convert_database_user(user):
    return {
        '_id': user['_id'],
        'username': user['username'],
        'isOfficial': user['isOfficial'],
        'lmsEnabled': user['lmsEnabled'],
        'tiers': {
            'easy': convert_user_tier_list(user['easyTasks']),
            'medium': convert_user_tier_list(user['mediumTasks']),
            'hard': convert_user_tier_list(user['hardTasks']),
            'elite': convert_user_tier_list(user['eliteTasks']),
            'passive': convert_user_tier_list(user['passiveTasks']),
            'extra': convert_user_tier_list(user['extraTasks']),
            'bossPets': convert_user_tier_list(user['bossPetTasks']),
            'skillPets': convert_user_tier_list(user['skillPetTasks']),
            'otherPets': convert_user_tier_list(user['otherPetTasks'])
        }
    }

'''
migrate_db:

Migrates all users to new format in a new table called taskLists
'''
def migrate_db():
    coll = mydb['taskAccounts']
    new_coll = mydb['taskLists'] # Can't seem to find a way to easily rewrite to existing collection
    new_coll.drop()

    users = coll.find({}, {})

    for user in users:
        new_coll.insert_one(convert_database_user(user))


if __name__ == "__main__":
    migrate_db()
    print(get_taskCurrent('musto1'))