import json
from dataclasses import dataclass

@dataclass
class ColLogData:
    category: str
    log_name: str
    exclude: list
    include: list
    log_count: int
    count: int

@dataclass
class Task:
    id: int
    name: str
    tip: str
    is_lms: str
    wiki_link: str
    wiki_image: str
    asset_image: str
    col_log_data: ColLogData


def to_col_log_data(data):
    if data is None:
        return None
    return ColLogData(category=data['category'],
                      log_name=data['logName'],
                      exclude=data.get('exclude'),
                      include=data.get('include'),
                      log_count=data['logCount'],
                      count=data.get('count'))

def to_task_class(data):
    return Task(id=data['_id'],
                name=data['name'],
                tip=data.get('tip'),
                is_lms=data.get("isLMS") is True,
                wiki_link=data['wikiLink'],
                wiki_image=data.get('wikiImage'),
                asset_image=data['assetImage'],
                col_log_data=to_col_log_data(data.get('colLogData'))
                )

def convert_dicts(l):
    return list(map(to_task_class, l))

def read_tasks(filename):
    with open('tasks/' + filename + '.json') as f:
        json_list = json.load(f)
        return list(map(to_task_class, json_list))


easy = read_tasks('easy')
medium = read_tasks('medium')
hard = read_tasks('hard')
elite = read_tasks('elite')
passive = read_tasks('passive')
extra = read_tasks('extra')
boss_pet = read_tasks('bossPets')
skill_pet = read_tasks('skillPets')
other_pet = read_tasks('otherPets')
