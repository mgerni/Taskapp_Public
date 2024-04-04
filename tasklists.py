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
bossPets = read_tasks('bossPets')
skillPets = read_tasks('skillPets')
otherPets = read_tasks('otherPets')

# TODO Should we create a task class?
