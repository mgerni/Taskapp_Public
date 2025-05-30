from dataclasses import dataclass
from datetime import datetime

@dataclass
class ColLogData:
    category: str
    log_name: str
    exclude: list
    include: list
    multi_category: list
    multi: list
    log_count: int
    count: int

@dataclass
class TaskData:
    id: int
    name: str
    tip: str
    is_lms: str
    wiki_link: str
    wiki_image: str
    asset_image: str
    col_log_data: ColLogData
    uuid: str

@dataclass
class UserCurrentTask:
    uuid: str
    task_id: int = None
    assigned_date: datetime = None

@dataclass
class UserCompletedTask:
    uuid: str
    task_id: int = None
    assigned_date: datetime = None
    completed_date: datetime = None

@dataclass
class UserTaskList:
    current_task: UserCurrentTask
    completed_tasks: list[UserCompletedTask]

@dataclass
class TierProgress:
    percent_complete: int
    total: int
    total_complete: int

class PageTask:
    def __init__(self, is_completed: bool, is_current: bool, task_data: TaskData):
        self.name = task_data.name
        self.asset_image = task_data.asset_image
        self.is_completed = is_completed
        self.id = task_data.id
        self.is_current = is_current
        self.wiki_link = task_data.wiki_link
        self.tip = task_data.tip
        self.uuid = task_data.uuid

@dataclass
class LeaderboardEntry:
    username: str
    lms_enabled: bool
    easy_progress: TierProgress
    medium_progress: TierProgress
    hard_progress: TierProgress
    elite_progress: TierProgress
    master_progress : TierProgress

    # TODO Have different weightings per tier
    def points(self) -> int:
        return self.easy_progress.percent_complete + self.medium_progress.percent_complete + \
            self.hard_progress.percent_complete + self.elite_progress.percent_complete

