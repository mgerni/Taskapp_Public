import tasklists


def get_task_tip(new_task):
    return new_task['tip']


easy_tips = list(map(get_task_tip, tasklists.easy))
medium_tips = list(map(get_task_tip, tasklists.medium))
hard_tips = list(map(get_task_tip, tasklists.hard))
elite_tips = list(map(get_task_tip, tasklists.elite))
