from dataclasses import dataclass
from datetime import datetime

@dataclass
class ColLogData:
    category: str
    log_name: str
    exclude: list
    include: list
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

@dataclass
class UserCurrentTask:
    task_id: int
    assigned_date: datetime = None

@dataclass
class UserCompletedTask:
    task_id: int
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
