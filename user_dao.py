from math import floor
import tasklists
from dataclasses import dataclass
from bson.objectid import ObjectId
from task_types import UserTaskList, TierProgress, UserCompletedTask, UserCurrentTask, TaskData


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
            'eliteTasks': self.elite,
            'easy': self.easy,
            'medium': self.medium,
            'hard': self.hard,
            'elite': self.elite
        }[tier]

    def current_task_for_tier(self, tier: str) -> tuple or None:
        user_task_list = self.get_task_list(tier)
        if user_task_list.current_task is None:
            return None
        task = task_info_for_id(tasklists.list_for_tier(tier), user_task_list.current_task.task_id)
        # TODO Fix this format
        return task.name, task.asset_image, tier, task.id, task.tip, task.wiki_link, task.wiki_image

    def current_task(self) -> tuple or None:
        if self.easy.current_task is not None:
            return self.current_task_for_tier('easyTasks')
        elif self.medium.current_task is not None:
            return self.current_task_for_tier('mediumTasks')
        elif self.hard.current_task is not None:
            return self.current_task_for_tier('hardTasks')
        elif self.elite.current_task is not None:
            return self.current_task_for_tier('eliteTasks')
        else:
            return None

    def get_tier_progress(self, tier: str) -> TierProgress:
        completed = len(self.get_task_list(tier).completed_tasks)
        total_tasks = tasklists.list_for_tier(tier, self.lms_enabled)
        total = len(total_tasks)
        percent = floor(completed / total * 100)
        return TierProgress(percent, total, completed)


def task_info_for_id(task_list: list[TaskData], task_id: [str]) -> tasklists.TaskData:
    filtered = list(filter(lambda x: x.id == task_id, task_list))
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
        completed_tasks = list(map(lambda x: UserCompletedTask(task_id=x['taskId']), data['completedTasks']))
        # Filter tasks that have been removed from tasklist
        all_current_tier_ids = list(map(lambda x: x.id, tasklists.list_for_tier(tier)))
        completed_tasks = list(filter(lambda x: x.task_id in all_current_tier_ids, completed_tasks))

        current = data.get('currentTask')
        if current:
            current = UserCurrentTask(task_id=current['taskId'])
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
        passive=convert_database_tier('passive'),
        extra=convert_database_tier('extra'),
        boss_pets=convert_database_tier('bossPets'),
        skill_pets=convert_database_tier('skillPets'),
        other_pets=convert_database_tier('otherPets')
    )
