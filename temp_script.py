import task_tips
import task_urls
import task_images
import collection_log
import old_tasklist
import json

#
#  Temporary Script to generate Task JSON data
#


completions = [
    old_tasklist.easy,
    old_tasklist.medium,
    old_tasklist.hard,
    old_tasklist.elite,
    old_tasklist.boss_pet,
    old_tasklist.skill_pet,
    old_tasklist.other_pet,
    old_tasklist.extra,
    old_tasklist.passive,
    task_urls.easy_urls,
    task_urls.medium_urls,
    task_urls.hard_urls,
    task_urls.elite_urls,
    task_urls.boss_pet_urls,
    task_urls.skilling_pet_urls,
    task_urls.other_pet_urls,
    task_urls.extra_urls,
    task_urls.passive_urls,
    task_tips.easy_tips,
    task_tips.medium_tips,
    task_tips.hard_tips,
    task_tips.elite_tips,
    task_images.easy_images,
    task_images.medium_images,
    task_images.hard_images,
    task_images.elite_images
]

def combine_tasks_with_col_log_data(tasks, wiki_urls, tips, images, col_log_data_list):
    new_tasks = []
    i = 1
    for task, url, tip, wikiImage, col_log_data in zip(tasks, wiki_urls, tips, images, col_log_data_list):
        col_log_data['logCount'] = col_log_data.pop('db_count')
        new_tasks.append(
            {
                "_id": i,
                "name": list(task.keys())[0],
                "isLms": list(task.values())[1],
                "tip": tip,
                "wikiLink": url,
                "wikiImage": wikiImage['taskImage'],
                "assetImage": list(task.values())[0],
                "colLogData": {x: col_log_data[x] for x in col_log_data if x not in { 'taskName', 'log_count' }}
            }
        )
        i += 1
    return new_tasks

def combine_tasks(tasks, wiki_urls, tips, images):
    new_tasks = []
    i = 1
    for task, url, tip, wikiImage in zip(tasks, wiki_urls, tips, images):
        new_tasks.append(
            {
                "_id": i,
                "name": list(task.keys())[0],
                "isLms": list(task.values())[1],
                "tip": tip,
                "wikiLink": url,
                "wikiImage": wikiImage['taskImage'],
                "assetImage": list(task.values())[0]
            }
        )
        i += 1
    return new_tasks

def combine_tasks_no_tip(tasks, wiki_urls):
    new_tasks = []
    for i, (task, url) in enumerate(zip(tasks, wiki_urls)):
        new_tasks.append(
            {
                "_id": i + 1,
                "name": list(task.keys())[0],
                "isLms": False if len(list(task.values())) == 1 else list(task.values())[1],
                "assetImage": list(task.values())[0],
                "wikiLink": url
            }
        )
    return new_tasks

class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
def write_dict_as_json(dict, fileName):
    with open(fileName, 'w') as f:
        json.dump(dict, f, indent=4, cls=SetEncoder)


if __name__ == "__main__":
    easyTasks = combine_tasks_with_col_log_data(completions[0], completions[9], completions[18], completions[22], collection_log.easy_log_slots)
    mediumTasks = combine_tasks_with_col_log_data(completions[1], completions[10], completions[19], completions[23], collection_log.medium_log_slots)
    hardTasks = combine_tasks_with_col_log_data(completions[2], completions[11], completions[20], completions[24], collection_log.hard_log_slots)
    eliteTasks = combine_tasks(completions[3], completions[12], completions[21], completions[25])
    bossPetTasks = combine_tasks_no_tip(completions[4], completions[13])
    skillPetTasks = combine_tasks_no_tip(completions[5], completions[14])
    otherPetTasks = combine_tasks_no_tip(completions[6], completions[15])
    extraTasks = combine_tasks_no_tip(completions[7], completions[16])
    passiveTasks = combine_tasks_no_tip(completions[8], completions[17])

    write_dict_as_json(easyTasks, "tasks/easy.json")
    write_dict_as_json(mediumTasks, "tasks/medium.json")
    write_dict_as_json(hardTasks, "tasks/hard.json")
    write_dict_as_json(eliteTasks, "tasks/elite.json")
    write_dict_as_json(bossPetTasks, "tasks/bossPets.json")
    write_dict_as_json(skillPetTasks, "tasks/skillPets.json")
    write_dict_as_json(otherPetTasks, "tasks/otherPets.json")
    write_dict_as_json(extraTasks, "tasks/extra.json")
    write_dict_as_json(passiveTasks, "tasks/passive.json")




