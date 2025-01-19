import json
from task_types import TaskData, ColLogData
def to_col_log_data(data: dict) -> ColLogData or None: # type: ignore
    if data is None:
        return None
    return ColLogData(category=data['category'],
                      log_name=data['logName'],
                      exclude=data.get('exclude'),
                      include=data.get('include'),
                      multi=data.get('multi'),
                      log_count=data['logCount'],
                      count=data.get('count'))

def to_task_class(data: dict) -> TaskData:
    return TaskData(id=data['_id'],
                    name=data['name'],
                    tip=data.get('tip'),
                    is_lms=data.get("isLMS") is True,
                    wiki_link=data['wikiLink'],
                    wiki_image=data.get('wikiImage'),
                    asset_image=data['assetImage'],
                    col_log_data=to_col_log_data(data.get('colLogData'))
                    )

def read_tasks(filename: str) -> list[TaskData]:
    with open('tasks/' + filename + '.json') as f:
        json_list = json.load(f)
        return list(map(to_task_class, json_list))


easy = read_tasks('easy')
medium = read_tasks('medium')
hard = read_tasks('hard')
elite = read_tasks('elite')
master = read_tasks('master')
passive = read_tasks('passive')
extra = read_tasks('extra')
boss_pet = read_tasks('bossPets')
skill_pet = read_tasks('skillPets')
other_pet = read_tasks('otherPets')

#
def list_for_tier(tier: str, include_lms: bool = True) -> list[TaskData]:
    all_tasks = {
        'easyTasks': easy,
        'mediumTasks': medium,
        'hardTasks': hard,
        'eliteTasks': elite,
        'masterTasks' : master,
        'passive': passive,
        'extra': extra,
        'bossPets': boss_pet,
        'skillPets': skill_pet,
        'otherPets': other_pet,
        'easy': easy,
        'medium': medium,
        'hard': hard,
        'elite': elite,
        'master': master
    }[tier]
    if not include_lms:
        return list(filter(lambda x: not x.is_lms, all_tasks))
    return all_tasks
