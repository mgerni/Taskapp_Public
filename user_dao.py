from math import floor
import tasklists
from dataclasses import dataclass
from bson.objectid import ObjectId
from task_types import UserTaskList, TierProgress, UserCompletedTask, UserCurrentTask, TaskData, PageTask
from uuid import UUID

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
    master: UserTaskList
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
            'eliteTasks': self.elite,
            'masterTasks': self.master,
            'easy': self.easy,
            'medium': self.medium,
            'hard': self.hard,
            'elite': self.elite,
            'master': self.master,
            'passive': self.passive,
            'extra': self.extra,
            'bossPets': self.boss_pets,
            'skillPets': self.skill_pets,
            'otherPets': self.other_pets,
        }[tier]
    

    def current_task_for_tier(self, tier: str) -> tuple or None: # type: ignore
        user_task_list = self.get_task_list(tier)
        if user_task_list.current_task is None:
            return None
        task = task_info_for_id(tasklists.list_for_tier(tier), user_task_list.current_task.uuid)
        # TODO Fix this format
        return task.name, task.asset_image, tier, task.uuid, task.tip, task.wiki_link, task.wiki_image

    def current_task(self) -> tuple or None: # type: ignore
        if self.easy.current_task is not None:
            return self.current_task_for_tier('easyTasks')
        elif self.medium.current_task is not None:
            return self.current_task_for_tier('mediumTasks')
        elif self.hard.current_task is not None:
            return self.current_task_for_tier('hardTasks')
        elif self.elite.current_task is not None:
            return self.current_task_for_tier('eliteTasks')
        elif self.master.current_task is not None:
            return self.current_task_for_tier('masterTasks')
        else:
            return None

    def get_tier_progress(self, tier: str) -> TierProgress:
        # remove instance of duplicate uuid in completed tasks
        def clean_tasklists(tier: str):
            tasklist = self.get_task_list(tier)
            tasklist.completed_tasks = list({task.uuid: task for task in tasklist.completed_tasks}.values())
            if not self.lms_enabled:
                lms_uuids = {
                            "df3f714e-eb7e-4b86-8b73-f25d6ebc3020",
                            "bf07a401-9a81-4520-9dd8-1c5af2bc5986",
                            "69b50b44-33f2-485e-a4e0-195e8f8fa044",
                            "60cbbdb2-b233-48a0-8413-8867217ce53a",
                            "4ba185cd-ee9b-45ce-b2c9-10462a8ee843",
                            "0e7ab87d-cde1-4224-b731-0f4b16308e59",
                            "2cff2acd-a0c8-446b-a83b-9ac734b308ad",
                            "bc76ea57-5ef9-4ab0-bdcb-37c410c2183a",
                            "1cf06859-ff55-476e-9387-80ca82f480ca",
                            "5407a890-c3dd-4453-96a2-59f97fc98479",
                            "11f65391-8e33-49dc-bd81-47744eb34ed9",
                            "2a5428a2-a6a5-44fd-ad89-d8bb4d1cf516",
                            "116ba1f6-6416-4f8f-8e32-42f096b3fe04",
                            "ccf42f4a-78e9-4968-b696-b75522198ef4",
                            "fa5841dd-eb4f-4140-84aa-e10201e3f1cb",
                            "e218b954-430c-4baf-b2eb-aa174cddbfc7",
                            "655a77fa-21f6-43e8-9cde-5eb2b660f829",
                            "347d5712-ebc3-4b74-8aba-ba909c39013e",
                            "2eb6623e-a326-4b63-9cae-8fa0823c5d49",
                            "50b61b0e-70d0-40a9-bf42-c1b8ac917717",
                            "917b912c-2716-4b12-a020-a758ee467e72",
                            "5cbcc790-10d1-4c17-8b39-cad7b48dadf8",
                            "4a387bb0-dfc3-4374-aa35-9bacfc2fc92d"
                            }
                lms_uuid_set = {UUID(u) for u in lms_uuids}
                tasklist.completed_tasks = [
                    task for task in tasklist.completed_tasks
                    if UUID(task.uuid) not in lms_uuid_set
                ]
            print("-"*100)
            print(tasklist)
            print("-"*100)
            return tasklist
        completed = len(clean_tasklists(tier).completed_tasks)
        
        # completed = len(self.get_task_list(tier).completed_tasks)
        total_tasks = tasklists.list_for_tier(tier, self.lms_enabled)
        total = len(total_tasks)
        percent = floor(completed / total * 100)
        print(f"Tier: {tier}, Completed: {completed}, Total: {total}, Percent: {percent}%")
        return TierProgress(percent, total, completed)

    def page_tasks(self, tier: str) -> list[PageTask]:
        if tier in ['easy', 'medium', 'hard', 'elite', 'master']:
            current_task = self.current_task_for_tier(tier)
            current_task_id = current_task[3] if current_task is not None else None
        else:
            current_task_id = None
        completed_task_ids = list(map(lambda x: x.uuid, self.get_task_list(tier).completed_tasks))

        def page_task(task: TaskData):
            return PageTask(is_current=task.uuid is current_task_id, is_completed=task.uuid in completed_task_ids,
                            task_data=task)

        return list(map(page_task, tasklists.list_for_tier(tier, self.lms_enabled)))


def task_info_for_id(task_list: list[TaskData], task_id: str) -> tasklists.TaskData:
    filtered = list(filter(lambda x: x.uuid == task_id, task_list))
    if len(filtered) == 0:
        raise Exception("No id found in list " + task_id)
    return filtered[0]


'''
convert_database_user

Converts a dict object from the taskLists Mongo collection to a UserDatabaseObject

Args:
    dict: user_data - User data from MongoDB

Returns:
    UserDatabaseObject

'''


def convert_database_user(user_data: dict) -> UserDatabaseObject:
    tiers = user_data['tiers']

    def convert_database_tier(tier: str) -> UserTaskList:
        data = tiers[tier]
        if data:
            completed_tasks = list(map(lambda x: UserCompletedTask(uuid=x['uuid']), data['completedTasks']))
            # Filter tasks that have been removed from tasklist
            all_current_tier_ids = list(map(lambda x: x.uuid, tasklists.list_for_tier(tier)))
            completed_tasks = list(filter(lambda x: x.uuid in all_current_tier_ids, completed_tasks))
            # print(completed_tasks)
        current = data.get('currentTask', None)
        if current:
            current = UserCurrentTask(uuid=current['uuid'])
        return UserTaskList(current_task=current,
                            completed_tasks=completed_tasks)

    return UserDatabaseObject(
        id=user_data['_id'],
        username=user_data['username'],
        is_official=user_data['isOfficial'],
        lms_enabled=user_data['lmsEnabled'],
        easy=convert_database_tier('easy'),
        medium=convert_database_tier('medium'),
        hard=convert_database_tier('hard'),
        elite=convert_database_tier('elite'),
        master=convert_database_tier('master'),
        passive=convert_database_tier('passive'),
        extra=convert_database_tier('extra'),
        boss_pets=convert_database_tier('bossPets'),
        skill_pets=convert_database_tier('skillPets'),
        other_pets=convert_database_tier('otherPets')
    )
