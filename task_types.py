from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass
class VerificationData:
    method: str

# TODO: achievement diary and skill verification methods
@dataclass
class CollectionLogVerificationData(VerificationData):
    item_ids: list[int]
    count: int


@dataclass
class TaskData:
    id: str
    name: str
    tip: str
    wiki_link: str
    image_link: str
    tags: list["TaskTag"]
    verification: VerificationData

class TaskTag(Enum):
    LMS = "lms"


@dataclass
class UserCurrentTask:
    id: str
    assigned_date: datetime = None

@dataclass
class UserCompletedTask:
    id: str
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
        self.is_completed = is_completed
        self.id = task_data.id
        self.is_current = is_current
        self.wiki_link = task_data.wiki_link
        self.image_link = task_data.image_link
        self.tip = task_data.tip

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
