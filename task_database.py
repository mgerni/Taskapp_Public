import random
import gspread
import re
from math import floor
import tasklists
import config

mydb = config.MONGO_CLIENT["TaskApp"]

# Ideally, we don't store all of this in Mongo but here is a rewrite with the new tasklist changes to keep it compatible
def combine_tasks(tasks: list[tasklists.Task]):
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
    easyFirst: True/False,
    mediumFirst: True/False,
    hardFirst: True/False,
    eliteFirst: True/False,
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

    taskAccount = {
        "username": str(username),
        "isOfficial": bool(isOfficial),
        "lmsEnabled": bool(lmsEnabled),
        "easyTasks": combine_tasks(tasklists.easy),
        "mediumTasks": combine_tasks(tasklists.medium),
        "hardTasks": combine_tasks(tasklists.hard),
        "eliteTasks": combine_tasks(tasklists.elite),
        "bossPetTasks": combine_tasks(tasklists.boss_pet),
        "skillPetTasks": combine_tasks(tasklists.skill_pet),
        "otherPetTasks": combine_tasks(tasklists.other_pet),
        "extraTasks": combine_tasks(tasklists.extra),
        "passiveTasks": combine_tasks(tasklists.passive),
        "easyFirst": False,
        "hardFirst": False,
        "mediumFirst": False,
        "eliteFirst": False
    }

    coll.insert_one(taskAccount)

# NOT USED, generic function to list all documents in a collection. Used for testing.
def query_coll(collection):
    coll = mydb[collection]
    finder = coll.find()
    for x in finder:
        print(x)

# NOT USED, generic function to delete/drop an entire collection. Used for testing.
def delete_coll(collection):
    mycol = mydb[collection]
    mycol.drop()



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
    task_list = ['easyTasks', 'mediumTasks', 'hardTasks', 'eliteTasks']
    coll = mydb['taskAccounts']
    user_info = coll.find({'username': username})
    for info in user_info:
        for tier in task_list:
            task_tier = tier
            for task in info[tier]:
                if task['taskCurrent'] == True:
                    taskcurrent_id = task['_id']
                    task_tip = task['taskTip']
                    wiki_url = task['wikiLink']
                    wiki_image = task['taskImage']
                    for taskname , taskimage in task['taskname'].items():
                        return taskname, taskimage, task_tier ,taskcurrent_id, task_tip, wiki_url, wiki_image


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
    coll = mydb['taskAccounts']
    user_info = coll.find({'username': username}, {tier: 1})
    for task in user_info:
        for ele in task[tier]:
            if ele['taskCurrent'] == True:
                taskcurrent_id = ele['_id']
                task_tip = ele['taskTip']
                wiki_url = ele['wikiLink']
                for taskname, taskimage in ele['taskname'].items():
                    return taskname, taskimage, tier, taskcurrent_id, task_tip, wiki_url



'''
lms_check:

The lms_check function, checks if user has lms enabled.


Args:
    str: username - username of the user.

Returns:
    bool: True if lms is enabled, False if not.

'''
def lms_check(username):
    coll = mydb['taskAccounts']
    lms = coll.find_one({'username': username}, {'lmsEnabled': True})
    return lms['lmsEnabled']


'''
official_check:

The official_check function, checks if user is official.


Args:
    str: username - username of the user.

Returns:
    bool: True if official, False if not.

'''
def official_check(username):
    coll = mydb['taskAccounts']
    official = coll.find_one({'username': username}, {'isOfficial' : True})
    return official['isOfficial']

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
    coll = mydb['taskAccounts']
    tasks_list = []
    lms_enabled = lms_check(username)
    if get_taskCurrent_tier(username, tier) is None:
        task_query = coll.find({'username': username}, {tier: 1})
        for task in task_query:
            for ele in task[tier]:
                if ele['status'] == 'Incomplete':
                    tasks_list.append(ele)
                    if lms_enabled is False and ele['taskname']['LMS'] is True:
                        tasks_list.remove(ele)
    if len(tasks_list) != 0:
        generated_task = random.choice(tasks_list)

        coll.update_one({'username': username , '%s._id' % tier : generated_task['_id']}, {'$set' : {'%s.$.taskCurrent' % tier: True }})
    else:
        task_info = get_taskCurrent_tier(username, tier)
        task_tier = task_info[2]
        task_number = task_info[3]
        coll.update_one({'username': username, '%s._id' % task_tier : task_number}, {'$set' : {'%s.$.taskCurrent' % tier: False }})


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

    coll = mydb['taskAccounts']
    tasks_easy = []
    tasks_medium = []
    tasks_hard = []
    tasks_elite = []
    if get_taskCurrent(username) is None:
        task_query = coll.find({'username': username}, {'easyTasks': 1, 'mediumTasks': 1, 'hardTasks': 1, 'eliteTasks': 1})

        for task in task_query:
            for ele in task['easyTasks']:
                if ele['status'] == 'Incomplete':
                    if lms_check(username):
                            tasks_easy.append(ele)
                    else:
                        if ele['taskname']['LMS'] == False:
                            tasks_easy.append(ele)

            for ele in task['mediumTasks']:
                if ele['status'] == 'Incomplete':
                    if lms_check(username):
                            tasks_medium.append(ele)
                    else:
                        if ele['taskname']['LMS'] == False:
                            tasks_medium.append(ele)

            for ele in task['hardTasks']:
                if ele['status'] == 'Incomplete':
                    if lms_check(username):
                            tasks_hard.append(ele)
                    else:
                        if ele['taskname']['LMS'] == False:
                            tasks_hard.append(ele)

            for ele in task['eliteTasks']:
                if ele['status'] == 'Incomplete':
                    if lms_check(username):
                            tasks_elite.append(ele)
                    else:
                        if ele['taskname']['LMS'] == False:
                            tasks_elite.append(ele)

        if len(tasks_easy) != 0:
            generated_task = random.choice(tasks_easy)
            coll.update_one({'username': username , 'easyTasks._id' : generated_task['_id']}, {'$set' : {'easyTasks.$.taskCurrent': True }})
        elif len(tasks_medium) != 0:
            generated_task = random.choice(tasks_medium)
            coll.update_one({'username': username , 'mediumTasks._id' : generated_task['_id']}, {'$set' : {'mediumTasks.$.taskCurrent': True }})

        elif len(tasks_hard) != 0:
            generated_task = random.choice(tasks_hard)
            coll.update_one({'username': username , 'hardTasks._id' : generated_task['_id']}, {'$set' : {'hardTasks.$.taskCurrent': True }})

        elif len(tasks_elite) != 0:
            generated_task = random.choice(tasks_elite)
            coll.update_one({'username': username , 'eliteTasks._id' : generated_task['_id']}, {'$set' : {'eliteTasks.$.taskCurrent': True }})





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
    easy_first, medium_first, hard_first, elite_first = False, False, False, False
    progress_before = get_task_progress(username)
    easy_before, medium_before, hard_before, elite_before = progress_before[0], progress_before[1], progress_before[2], progress_before[3]

    coll.update_one({'username': username , '%s._id' % tier : task_id}, {'$set' : {'%s.$.status' % tier: 'Complete', '%s.$.taskCurrent' % tier: False }})

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
                    task_id= task['_id']
                    coll.update_one({'username' : username, '%s._id' % tier : task_id}, {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier : 'Incomplete'}})
    task_check = get_taskCurrent(username)
    if task_check is not None:
        tier = task_check[2]
        task_id = task_check[3]
        coll.update_one({'username' : username, '%s._id' % tier : task_id}, {'$set': {'%s.$.taskCurrent' % tier: False, '%s.$.status' % tier : 'Incomplete'}})




# DEPRECATED see reindex_list_one()
def reindex_list(tier):
    coll = mydb['taskAccounts']
    user_info = coll.find({}, {"_id" : 0, tier: 1})
    for info in user_info:
        i = 1
        for index, task in enumerate(info[tier]):
            coll.update_many({"%s._id" % tier : task["_id"]}, {"$set": {"%s.%s._id" % (tier, index): i}})
            i += 1


'''
reindex_list_one:

The reindex_list_one function, reindexes the _id for each task in a given tier for all users. 
This is used when a task is removed or added to the list.
Only updates a task _id if the is out of sync with the pointer. 


Args:
    str: tier - The tier of the task list to reindex.

# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:

'''
def reindex_list_one(tier):
    coll = mydb['taskAccounts']
    user_info = coll.find({}, {"_id" : 0, tier: 1})
    for info in user_info:
        i = 1
        for index, task in enumerate(info[tier]):

            if task['_id'] == i:
                print('No need to reindex task: %s ... Skipping' % task['_id'])
                i += 1
            else:
                print('Reindexing... %s' % task['_id'])
                coll.update_many({"%s._id" % tier : task["_id"]}, {"$set": {"%s.%s._id" % (tier, index): i}})
                i += 1

def reindex_list_two(tier):
    coll = mydb['taskAccounts']
    user_info = coll.find({}, {"_id" : 0, tier: 1, "username": 1})
    for count, info in enumerate(user_info, 1):
        print(info['username'])
        print(f"[{count}]: {info['username']}")
        i = 1
        new_task_list = []
        for task_list in info[tier]:
            if i != task_list['_id']:
                task_list['_id'] = i
            i += 1
            new_task_list.append(task_list)
        coll.update_one({'username': info['username']}, {'$set': {tier: new_task_list}})

'''
rename_task:

The rename_task function, overwrites the taskname dictionary.


Args:
    str: tier - The tier the task belongs to.
    int: task_id - The _id of the task. 
    str: new_name - The new task name. 
    str: new_image - The new image.
    bool: lms_bool - wether the task is an LMS task or not.
    str : new_tip - The new tip of the task.
    str : new_wiki_link - The new wiki link of the task. 
    str : new_task_image - The new wiki image for the task. 


# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:

'''

def rename_task(tier, task_id, new_name, new_image, lms_bool , new_tip, new_wiki_link, new_task_image):
    coll = mydb['taskAccounts']
    update = coll.update_many({'%s._id' % tier: task_id},
        {'$set':
            {
                '%s.$.taskname'% tier:
                    {
                        new_name: new_image,
                        "LMS": lms_bool,
                    },
                f"{tier}.$.taskTip" : new_tip,
                f"{tier}.$.wikiLink" : new_wiki_link,
                f"{tier}.$.taskImage" : new_task_image
            }
        }
    )

    print(update.raw_result)


'''
update_tip:

The update_tip function, changes the tip for a task.


Args:
    str: tier - The tier the task belongs to.
    int: task_id - The _id of the task. 
    str: new_tip - new tip. 


# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:

'''

def update_tip(tier, task_id, new_tip):
    coll = mydb['taskAccounts']
    update = coll.update_many({'%s._id' % tier: task_id}, {'$set': {'%s.$.taskTip'% tier: new_tip}})
    print(update.raw_result)



# NOT IN USE - left in for examples sake
def update_user(username, email):
    db = config.MONGO_CLIENT["TaskAppLoginDB"]
    coll = db['users']
    coll.update_one({'username': username}, {'$set':{ 'user_email' : email}})

# NOT IN USE - left in for examples sake
def update_all_users():
    coll = mydb['taskAccounts']
    for x in coll.find():
        username = x['username']

        coll.update_one({'username': username}, {'$set' : {'easyFirst': False, 'mediumFirst' : False, 'hardFirst': False, 'eliteFirst': False}})


# One-off function to add object to all Lists in the database.
# Should be modified for future use - left in for examples sake
def update_tip_url():
    coll = mydb['taskAccounts']
    for users in coll.find():
        user = users['username']
        for task in tasklists.easy:
            coll.update_one({'username': user, 'easyTasks._id': task.id},
            {'$set':{'easyTasks.$.taskTip': task.tip, 'easyTasks.$.wikiLink': task.wiki_link}})

        for task in tasklists.medium:
            coll.update_one({'username': user, 'mediumTasks._id': task.id},
            {'$set':{'mediumTasks.$.taskTip': task.tip, 'mediumTasks.$.wikiLink':  task.wiki_link}})

        for task in tasklists.hard:
            coll.update_one({'username': user, 'hardTasks._id': task.id},
            {'$set':{'hardTasks.$.taskTip': task.tip, 'hardTasks.$.wikiLink':  task.wiki_link}})

        for task in tasklists.elite:
            coll.update_one({'username': user, 'eliteTasks._id': task.id},
            {'$set':{'eliteTasks.$.taskTip': task.tip, 'eliteTasks.$.wikiLink':  task.wiki_link}})

        for task in tasklists.boss_pet:
            coll.update_one({'username': user, 'bossPetTasks._id': task.id},
            {'$set':{'bossPetTasks.$.wikiLink': task.wiki_link}})

        for task in tasklists.other_pet:
            coll.update_one({'username': user, 'otherPetTasks._id': task.id},
            {'$set':{'otherPetTasks.$.wikiLink': task.wiki_link}})

        for task in tasklists.other_pet:
            coll.update_one({'username': user, 'skillPetTasks._id': task.id},
            {'$set':{'skillPetTasks.$.wikiLink': task.wiki_link}})

        for task in tasklists.extra:
            coll.update_one({'username': user, 'extraTasks._id': task.id},
            {'$set':{'extraTasks.$.wikiLink': task.wiki_link}})

        for task in tasklists.passive:
            coll.update_one({'username': user, 'passiveTasks._id': task.id},
            {'$set':{'passiveTasks.$.wikiLink': task.wiki_link}})




'''
add_task_last:

The add_task_last function, adds a task to the end of a given tier list for all users.


Args:
    str: tier - The tier of the task list to add the task to.
    int: id - The id of the task to add. +=1 to the last id in the list.
    str: taskName - The name of the task to add.
    str: imagename - The name of the image to add.
    bool: lms - Whether the task is a LMS task or not.
    str: tip - The tip for the task.
    str: wikiLink - The wiki link for the task.

# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:


'''
def add_task_last(tier, id, task_name, task_image, lmsbool, tip, wikilink, url_image):
    coll = mydb['taskAccounts']
    coll.update_many(
        {},
    {"$push": {tier:
        {
        "_id": id,
        "taskname": {
            task_name: task_image,
            "LMS": lmsbool
        },
        "status": "Incomplete",
        "taskCurrent": False,
        "taskTip": tip,
        "wikiLink": wikilink,
        "taskImage": url_image
    }}})

'''
add_task_last_notip:

The add_task_last_notip function, adds a task to the list without a taskTip.


Args:
    str: tier - The tier of the task list to add the task to.
    int: id - The id of the task to add. +=1 to the last id in the list.
    str: task_name - The name of the task to add.
    str: task_image - The name of the image to add.
    bool: lmsbool - Whether the task is a LMS task or not.
    str: wikiLink - The wiki link for the task.

# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:


'''
def add_task_last_notip(tier, id, task_name, task_image, lmsbool, wikiLink):
    coll = mydb['taskAccounts']
    update = coll.update_many(
        {},
    {"$push": {tier:
        {
        "_id": id,
        "taskname": {
            task_name: task_image,
            "LMS": lmsbool
        },
        "status": "Incomplete",
        "taskCurrent": False,
        "wikiLink": wikiLink
    }
    }}

    )
    print(update.raw_result)

'''
add_task_postional:

The add_task_postional function, adds a task in a specific position of a given tier list for all users.
Used when Tedious adds tasks to the middle of the spreadsheet which sucks ass.


Args:
    str: tier - The tier of the task list to add the task to.
    int: id - The id of the task to add.
    str: taskName - The name of the task to add.
    str: imagename - The name of the image to add.
    bool: lms - Whether the task is a LMS task or not.
    str: tip - The tip for the task.
    str: wikiLink - The wiki link for the task.

# currently not used on the website only ran locally against the Database.
# TODO: add tip and wikiLink. 
# TODO: make this function work on the website. Haven't had to use this since taskTips/wikiLinks were added. 
# TODO: Should be updated to use reindex_list_one()

Returns:


'''
def add_task_postional(tier, id, task_name, task_image, lmsbool, position, task_tip, wiki_link, taskImage):
    coll = mydb['taskAccounts']
    coll.update_many(
        {},
        {
            "$push": {tier :{
                "$each": [{
                    "_id": id,
                    "taskname": {
                        task_name: task_image,
                        "LMS": lmsbool
                    },
                    "status": "Incomplete",
                    "taskCurrent": False,
                    "taskTip": task_tip,
                    "wikiLink": wiki_link,
                    "taskImage" : taskImage
                }],
                "$position": position
            }

            }
        }
    )
    reindex_list_two(tier)


'''
add_task_postional_notip:

The add_task_postional_notip function, adds a task in a specific position of a given tier list for all users.
Used when Tedious adds tasks to the middle of the spreadsheet which sucks ass.


Args:
    str: tier - The tier of the task list to add the task to.
    int: id - The id of the task to add.
    str: taskName - The name of the task to add.
    str: imagename - The name of the image to add.
    bool: lms - Whether the task is a LMS task or not.
    int: position - List/Array index to push at.
    str: wikiLink - The wiki link for the task.

# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website. Haven't had to use this since taskTips/wikiLinks were added. 
'''

def add_task_postional_notip(tier, id, task_name, task_image, lmsbool, position, wiki_link):
    coll = mydb['taskAccounts']
    coll.update_many(
        {},
        {
            "$push": {tier :{
                "$each": [{
                    "_id": id,
                    "taskname": {
                        task_name: task_image,
                        "LMS": lmsbool
                    },
                    "status": "Incomplete",
                    "taskCurrent": False,
                    "wikiLink": wiki_link
                }],
                "$position": position
            }

            }
        }
    )
    reindex_list_two(tier)

'''
remove_task:

The remove_task function, removes a task from a given tier list for all users.

Args:
    str: tier - The tier of the task list to add the task to.
    int: id - The id of the task to add.

# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:
        None

'''
def remove_task(tier, taskid):
    coll = mydb['taskAccounts']
    coll.update_many({},
    { "$pull": { tier : { "_id": taskid }}})
    print('Reindexing %s' % tier)
    reindex_list_two(tier)


# NOT USED
def remove_last_task_one(username, tier):
    coll = mydb['taskAccounts']
    coll.update_one({'username': username},
    {"$pop": { tier : 1}}
    )

def remove_task_last(tier):
    coll = mydb['taskAccounts']
    coll.update_many({}, {'$pop': {tier : 1}})




'''
move_task:

The move_task function, moves an exisiting task from one tier to another.

Args:
    str: old_tier - The tier of the task to remove from. 
    str: new_tier - The tier of the task list to add the task to.
    int: id - The id of the task to add.
    int: position - The element position of the task in the new tier.


# currently not used on the website only ran locally against the Database.
# TODO: make this function work on the website.

Returns:
        None

'''
def move_task(old_tier, new_tier, task_id, position):
    coll = mydb['taskAccounts']
    task = coll.find({}, {old_tier:  1, 'username': 1})
    for user in task:
        result = user[old_tier][task_id - 1]
        username = user['username']
        print('Updating: %s' % username)
        print('Adding task %s to %s' % (result['taskname'], new_tier))
        coll.update_one({'username': username},
                        {
                "$push": {new_tier :{
                    "$each": [result],
                    "$position": position
                }

                }
            }
        )
        print('Task added to %s' % username)
    print('Removing task %s from %s' % (task_id, old_tier))
    remove_task(old_tier, task_id)
    print('Reindexing %s' % new_tier)
    reindex_list_two(new_tier)



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


def add_task_last_one(username, tier, id, task_name, task_image, lmsbool, tip, wikilink, taskImage):
    coll = mydb['taskAccounts']
    coll.update_one(
        {'username': username},
    {"$push": {tier:
        {
        "_id": id,
        "taskname": {
            task_name: task_image,
            "LMS": lmsbool
        },
        "status": "Incomplete",
        "taskCurrent": False,
        "taskTip": tip,
        "wikiLink": wikilink,
        "taskImage": taskImage
    }
    }}
    )
    print('Completed Task add for:', username)

def add_task_last_one_no_tip(username, tier, id, task_name, task_image, lmsbool, wikilink):
    coll = mydb['taskAccounts']
    update = coll.update_one(
        {'username': username},
            {"$push":
                {tier:
                    {
                    "_id": id,
                    "taskname": {
                        task_name: task_image,
                        "LMS": lmsbool
                    },
                    "status": "Incomplete",
                    "taskCurrent": False,
                    "wikiLink": wikilink
                    }
                }
            }
    )
    print('Completed Task add for:', username)


def check_task():
    coll = mydb['taskAccounts']
    user_data = coll.find({}, {'eliteTasks' : 1, 'username' : 1, '_id': 0})
    try:
        for i, data in enumerate(user_data):
            username = data['username']
            if data['eliteTasks'][159]['status'] == 'Complete':
                print(f'{i} {username} Last GotR task is completed.')
            if data['eliteTasks'][159]['taskCurrent'] == True:
                print(f'{i} {username} Last GotR task is Current task.')
    except Exception as e:
        print(f'{i} {username} ERROR: {e}')

def all_users_task_status(tier, task_id):
    coll = mydb['taskAccounts']
    user_data = coll.find({}, {tier: 1, 'username': 1})
    for x in user_data:
        if x[tier][task_id]['taskCurrent'] == True:
            print(x['username'])

if __name__ == "__main__":
    pass