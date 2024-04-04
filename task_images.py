import tasklists

def get_task_image(new_task):
    return {'taskImage': new_task['wikiImage']}


easy_images = list(map(get_task_image, tasklists.easy))
medium_images = list(map(get_task_image, tasklists.medium))
hard_images = list(map(get_task_image, tasklists.hard))
elite_images = list(map(get_task_image, tasklists.elite))
