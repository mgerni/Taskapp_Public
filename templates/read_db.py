import pymongo


mongo_uri = "mongodb://localhost:27017/"
myclient = pymongo.MongoClient(mongo_uri)


'''
Creates database if it does not exist and connects to the database
'''

db = myclient["TaskApp"]
coll = db['taskAccounts']


def read_user(username):
    user_info = coll.find({'username': username})
    for info in user_info:
        for tasks in info['easyTasks']:
            if tasks['taskCurrent'] == True:
                for taskname , taskimage in tasks['taskname'].items():

                    return taskname, taskimage

current_task = read_user('testUser')
print(current_task[0])
print(current_task[1])

