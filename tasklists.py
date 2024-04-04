import json


class ColLogData:
    def __init__(self, category: str, log_name: str, exclude: list, include: list, log_count: int, count: int):
        self.category = category
        self.log_name = log_name
        self.exclude = exclude
        self.include = include
        self.log_count = log_count
        self.count = count

class PageTask:
    def __init__(self, _id: int, name: str, tip: str, wiki_link: str, wiki_image: str,
                 asset_image: str, col_log_data: ColLogData):
        self._id = _id
        self.name = name
        self.tip = tip
        self.wiki_link = wiki_link
        self.wiki_image = wiki_image
        self.asset_image = asset_image
        self.col_log_data = col_log_data


def read_tasks(filename):
    with open('tasks/' + filename + '.json') as f:
        return json.load(f)


easy = read_tasks('easy')
medium = read_tasks('medium')
hard = read_tasks('hard')
elite = read_tasks('elite')
passive = read_tasks('passive')
extra = read_tasks('extra')
boss_pets = read_tasks('bossPets')
skill_pets = read_tasks('skillPets')
other_pets = read_tasks('otherPets')

# TODO Should we create a task class?
