import bcrypt
import pymongo
import re
from task_database import add_task_account
import tasklist
import task_urls
import task_tips
import task_images
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
import taskapp
from datetime import datetime
import os



# Mongodb URI
MONGO_URL = os.environ["MONGO_URI"]

# Determines if certificate is needed for PROD.
if os.environ["TASKAPP_DEV"] == "True":
    myclient = pymongo.MongoClient(MONGO_URL)
else:
    X509_CERT = os.environ["X509_CERT"]
    myclient = pymongo.MongoClient(MONGO_URL,
                     tls=True,
                     tlsCertificateKeyFile=X509_CERT)


# specifies database to use.
db = myclient["TaskAppLoginDB"]

# specifies collection to use in TaskAppLoginDB database.
coll = db['users']

# specifies database to use.
mydb = myclient["TaskApp"]

# specifies collection to use in TaskApp database.
mycoll = mydb['taskAccounts']

# List of lists of dictionaries for tasks and cooresponding urls/tips. 
completions = [
    tasklist.easy, 
    tasklist.medium, 
    tasklist.hard, 
    tasklist.elite, 
    tasklist.boss_pet, 
    tasklist.skill_pet, 
    tasklist.other_pet, 
    tasklist.extra, 
    tasklist.passive,
    task_urls.easy_urls,
    task_urls.medium_urls,
    task_urls.hard_urls,
    task_urls.elite_urls,
    task_urls.boss_pet_urls,
    task_urls.skilling_pet_urls,
    task_urls.other_pet_urls,
    task_urls.extra_urls,
    task_urls.passive_urls,
    task_tips.easy_tips,
    task_tips.medium_tips,
    task_tips.hard_tips,
    task_tips.elite_tips,
    task_images.easy_images, ## 22
    task_images.medium_images, ## 23
    task_images.hard_images, ## 24
    task_images.elite_images ## 25
    ]

'''
query_email function:

The query_email function finds one document matching the email address provided.

Args:
    str: email - email address to be queried.
Returns:
    dict: email_query - dictionary of the document matching the email address.


'''
def query_email(email):
    email_query = coll.find_one({'user_email': email})
    return email_query


'''
get_reset_token function:

The get_reset_token generates a Serializer object with the SECRET_KEY and the expiration time.
Used for password resets.

Args:
    str: username - username of the user to be reset.
Returns:
    Serializer: s - Serializer object with the username.


'''
def get_reset_token(username, expires=1800):
    s = Serializer(taskapp.app.config['SECRET_KEY'], expires)
    return s.dumps({'username': username}).decode('utf-8')

'''
verify_reset_token function:

The verify_reset_token loads token generated by get_reset_token and verifies the token if it is valid.
Used for password resets.

Args:
    token: token - token to be verified.
Returns:
    str: username - username of the user. if valid.
    None: if invalid/expired.


'''
def verify_reset_token(token):
    s = Serializer(taskapp.app.config['SECRET_KEY'])
    try:
        username = s.loads(token)['username']
        
    except:
        return None
    return username

'''
email_verify function:

The email_verify confirms if the email address of the user has been verified.

Args:
    str: username - username of the user.
Returns:
    Tuple: email_verified - bool: boolean value.
              user_email - str: email address of the user.


'''
def email_verify(username):
    email_verified = coll.find_one({'username': username}, {'_id' : 0, 'email_verified' : 1, 'user_email': 1})
    return email_verified['email_verified'], email_verified['user_email']



'''
get_email_verify_token function:

The get_email_verify_token generates a Serializer object with the SECRET_KEY and the expiration time.
Used for email verification.

Args:
    str: username - username of the user to be reset.
    str: email - email address of the user.
Returns:
    Serializer: s - Serializer object with the username and email address of the user.


'''
def get_email_verify_token(username, email, expires=1800):
    s = Serializer(taskapp.app.config['SECRET_KEY'], expires)
    return s.dumps({'username': username, 'email' : email}).decode('utf-8')


'''
verify_email_verify_token function:

The verify_email_verify_token loads token generated by get_email_verify_token and verifies the token if it is valid.
Used for password resets.

Args:
    token: token - token to be verified.
Returns:
    str: username - username of the user. if valid.
    None: if invalid/expired.


'''
def verify_email_verify_token(token):
    s = Serializer(taskapp.app.config['SECRET_KEY'])
    try:
        username = s.loads(token)['username']
        email = s.loads(token)['email']
    except:
        return None
    return username, email



'''
update_email function:

The update_email updates one document matching the username provided, with the email address provided.
Used for email verification.

Args:
    str: username - username of the user to be updated.
    str: email - new email address of the user.

Returns:
    


'''
def update_email(username, email):
    coll.update_one({'username': username}, {'$set' : {'user_email': email, 'email_verified': True}})



'''
add_user function:

The add_user function, validates the password matches the password Regex.
Verified no other usernames exist with the same username. 
Adds user to the database. Passwords are Hashed and salted. 

Args:
    str: username - username of the user.
    str: email - email address of the user.
    str: password - password(text) of the user.
    bool: Offical status of the user.
    bool: LMS status of the user. 

Returns:
    None: if user was added, else str: error message. 
    bool: success - boolean value.

'''
def add_user(username, password, email, isOfficial, lmsEnabled):
    success = False
    error = None
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@!%*#?&])[A-Za-z\d@!#%*?&]{8,20}$"
    pattern = re.compile(reg)
    match = re.search(pattern, password)
    if match:
        
        user_querydb = {'username': username}
        doc_count = coll.count_documents(user_querydb)
        if doc_count == 0:
            hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_input = {"username": username, "hashed_password": hashed_pass, "user_email" : email, 'email_verified' : False}
            coll.insert_one(user_input)
            add_task_account(username, completions, isOfficial, lmsEnabled )
            success = True
            
            return success, error
        else:
            
            error = 'Username already exists'
            return success, error
    else:
        
        error = 'Password does not meet requirements'
        return success, error



'''
change_password function:

The change_password function validates the password matches the Regex.
Hash and salts the new password and updates the database.

Args:
    str: username - username of the user to be updated.
    str: password - new password of the user.

Returns:
    None: if password was updated, else str: error message.
    bool: success - boolean value.

'''
def change_password(username, password):
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@!%*#?&])[A-Za-z\d@!#%*?&]{8,20}$"
    pattern = re.compile(reg)
    match = re.search(pattern, password)
    error = None
    success = False
    if match:
        hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        coll.update_one({'username' : username}, {'$set': {'hashed_password': hashed_pass}})
        success = True
        return success, error
    else:
        error = 'Password does not meet requirements'
        return success, error

'''
email_change function:

The email_change function updates one document matching the username provided, with the email address provided.
Sets email_verified to False. Requries user to verify email address.


Args:
    str: username - username of the user to be updated.
    str: email - new email address of the user.

Returns:
    

'''
def email_change(username, email):
    coll.update_one({'username': username}, {'$set': {'user_email': email, "email_verified": False}})



'''
username_change function:

The username_change function checks if the username provided is already taken.
If not, updates the username of the user.



Args:
    str: username - username of the user to be updated.
    str: new_username - new username of the user.

Returns:
    str: error - error message. if error. 
    bool: success - boolean value.
'''
def username_change(username, username_value):
    success, error = False, None
    doc_count_new_username = coll.count_documents({'username': username_value})
    if doc_count_new_username != 0:
        error = 'Username already exists'
        return error
    else:
        coll.update_one({'username': username}, {'$set': {'username': username_value}})
        # mycoll.update_one({'username': username}, {'$set': {'username': username_value}})
        
        success = True
        return success


# NOT YET IMPLEMENTED - To be used for highscores soon TM. 
def get_all_users():
    verified_users_list = []
    get_verified_users = coll.find({'email_verified': True}, {'_id': 0, 'username': 1})
    
    for user in get_verified_users:
        task_user = user['username']
        disallowed = {'Gerni', 'nfinch', 'sirmad@outlook.com.au'}
        if task_user not in disallowed:
            verified_users_list.append(task_user)

    return verified_users_list

# NOT YET IMPLEMENTED - To be used for highscores soon TM. 
def sort_users(verified_user_list):
    start_time = datetime.now()
    official_user_list = []
    unofficial_user_list = []
    official_highscores_list = []
    unofficial_highscores_list = []
    for user in verified_user_list:
        user_state = mycoll.find_one({'username': user}, {'_id': 0, 'isOfficial': 1})
        if user_state['isOfficial'] == True:
            official_user_list.append(user)
        elif user_state['isOfficial'] == False:
            unofficial_user_list.append(user)
    

    for official_user in official_user_list:
        easy_completed = 0
        medium_completed = 0
        hard_completed = 0
        elite_completed = 0
        pet_completed = 0
        extra_completed = 0
        
        easy_points = 0
        medium_points = 0
        hard_points = 0
        elite_points = 0
        pet_points = 0
        extra_points = 0

        task_query = mycoll.find({'username': official_user},
        {
            'easyTasks' : 1,
            'mediumTasks' : 1,
            'hardTasks' : 1,
            'eliteTasks' : 1,
            'extraTasks' : 1,
            'bossPetTasks' : 1,
            'skillPetTasks' : 1,
            'otherPetTasks' : 1
        })

        for task in task_query:
            for ele in task['easyTasks']:
                if ele['status'] == 'Complete':
                    easy_completed += 1
                    easy_points += 2500

            for ele in task['mediumTasks']:
                if ele['status'] == 'Complete':
                    medium_completed += 1
                    medium_points += 2501

            for ele in task['hardTasks']:
                if ele['status'] == 'Complete':
                    hard_completed += 1
                    hard_points += 2502      

            for ele in task['eliteTasks']:
                if ele['status'] == 'Complete':
                    elite_completed += 1
                    elite_points += 2503

            for ele in task['extraTasks']:
                if ele['status'] == 'Complete':
                    extra_completed += 1     
                    extra_points += 2504  

            for ele in task['bossPetTasks']:
                if ele['status'] == 'Complete':
                    pet_completed += 1
                    pet_points += 2505

            for ele in task['skillPetTasks']:
                if ele['status'] == 'Complete':
                    pet_completed += 1
                    pet_points += 2505

            for ele in task['otherPetTasks']:
                if ele['status'] == 'Complete':
                    pet_completed += 1  
                    pet_points += 2505

        tasks_total =  easy_completed +  medium_completed + hard_completed + elite_completed + pet_completed + extra_completed
        points_total = easy_points + medium_points + hard_points + elite_points +extra_points + pet_points
        official_highscores_list.append({
            'official_user' : official_user,
            'easy_completed' : easy_completed,
            'medium_completed' : medium_completed,
            'hard_completed' : hard_completed,
            'elite_completed' : elite_completed,
            'pet_completed' : pet_completed,
            'extra_completed' : extra_completed,
            'points_total' : points_total,
            'tasks_total' : tasks_total
        })



    for unofficial_user in unofficial_user_list:
        easy_completed = 0
        medium_completed = 0
        hard_completed = 0
        elite_completed = 0
        pet_completed = 0
        extra_completed = 0
        
        easy_points = 0
        medium_points = 0
        hard_points = 0
        elite_points = 0
        pet_points = 0
        extra_points = 0

        task_query = mycoll.find({'username': unofficial_user},
        {
            'easyTasks' : 1,
            'mediumTasks' : 1,
            'hardTasks' : 1,
            'eliteTasks' : 1,
            'extraTasks' : 1,
            'bossPetTasks' : 1,
            'skillPetTasks' : 1,
            'otherPetTasks' : 1
        })

        for task in task_query:
            for ele in task['easyTasks']:
                if ele['status'] == 'Complete':
                    easy_completed += 1
                    easy_points += 2500

            for ele in task['mediumTasks']:
                if ele['status'] == 'Complete':
                    medium_completed += 1
                    medium_points += 2501

            for ele in task['hardTasks']:
                if ele['status'] == 'Complete':
                    hard_completed += 1
                    hard_points += 2502      

            for ele in task['eliteTasks']:
                if ele['status'] == 'Complete':
                    elite_completed += 1
                    elite_points += 2503

            for ele in task['extraTasks']:
                if ele['status'] == 'Complete':
                    extra_completed += 1     
                    extra_points += 2504  

            for ele in task['bossPetTasks']:
                if ele['status'] == 'Complete':
                    pet_completed += 1
                    pet_points += 2505

            for ele in task['skillPetTasks']:
                if ele['status'] == 'Complete':
                    pet_completed += 1
                    pet_points += 2505

            for ele in task['otherPetTasks']:
                if ele['status'] == 'Complete':
                    pet_completed += 1  
                    pet_points += 2505

        tasks_total =  easy_completed +  medium_completed + hard_completed + elite_completed + pet_completed + extra_completed
        points_total = easy_points + medium_points + hard_points + elite_points +extra_points + pet_points
        unofficial_highscores_list.append({
            'unofficial_user' : unofficial_user,
            'easy_completed' : easy_completed,
            'medium_completed' : medium_completed,
            'hard_completed' : hard_completed,
            'elite_completed' : elite_completed,
            'pet_completed' : pet_completed,
            'extra_completed' : extra_completed,
            'points_total' : points_total,
            'tasks_total' : tasks_total
        })

    return official_highscores_list, unofficial_highscores_list


if __name__ == '__main__':
    pass
    # test = get_all_users()
    # sort_users(test)

