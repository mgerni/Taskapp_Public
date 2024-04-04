import json

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
