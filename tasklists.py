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
    wiki_link: str
    wiki_image: str
    asset_image: str
    col_log_data: ColLogData


def read_tasks(filename):
    with open('tasks/' + filename + '.json') as f:
        return json.load(f)

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
                wiki_link=data['wikiLink'],
                wiki_image=data.get('wikiImage'),
                asset_image=data['assetImage'],
                col_log_data=data.get('colLogData')
                )

def convert_dicts(l):
    return list(map(to_task_class, l))


# Deprecated - Use the new class lists below
# Exporting for backwards compatibility
easy = read_tasks('easy')
medium = read_tasks('medium')
hard = read_tasks('hard')
elite = read_tasks('elite')
passive = read_tasks('passive')
extra = read_tasks('extra')
boss_pets = read_tasks('bossPets')
skill_pets = read_tasks('skillPets')
other_pets = read_tasks('otherPets')

easy_tasks = convert_dicts(easy)
medium_tasks = convert_dicts(medium)
hard_tasks = convert_dicts(hard)
elite_tasks = convert_dicts(elite)
passive_tasks = convert_dicts(passive)
extra_tasks = convert_dicts(extra)
boss_pet_tasks = convert_dicts(boss_pets)
skill_pet_tasks = convert_dicts(skill_pets)
other_pet_tasks = convert_dicts(other_pets)
