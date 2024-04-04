import tasklists

def to_old_task(new_task):
    return {new_task['name']: new_task['assetImage'], 'LMS': 'isLMS' in new_task}


easy = list(map(to_old_task, tasklists.easy))
medium = list(map(to_old_task, tasklists.medium))
hard = list(map(to_old_task, tasklists.hard))
elite = list(map(to_old_task, tasklists.elite))
extra = list(map(to_old_task, tasklists.extra))
passive = list(map(to_old_task, tasklists.passive))
boss_pet = list(map(to_old_task, tasklists.boss_pets))
skill_pet = list(map(to_old_task, tasklists.skill_pets))
other_pet = list(map(to_old_task, tasklists.other_pets))