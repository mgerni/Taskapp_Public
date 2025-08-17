# Taskapp #

OSRS task tracker and generator

See live version - https://www.osrstaskapp.com/

## Initial Setup ###

### Install latest Python 3 version ###
`https://www.python.org/downloads/`

### Create a virtualenv ###
`python3 -m venv /path/`

### Activate virtualenv (Linux) ###
`source /path/bin/activate`

### Activate virtualenv (Windows) ###
`/path/Scripts/Activate.ps1`

### Create a sendgrind API account for free ###
https://sendgrid.com/en-us

### Create enviroment variables ###
For example
```
export FLASK_ENV=development
export MONGO_URI=mongodb://root:example@localhost:27017/
export SENDGRID_API_KEY=192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf
export SECRET_KEY=192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf
```

### Install dependencies ###
`pip install -r requirements.txt`

### MongoDB Setup - Local Testing ###
Follow instructions on `https://docs.mongodb.com/manual/administration/install-community/` to install mongoDB

Alternatively, if you use Docker, you can run a Mongo DB instance using `docker compose up`

In mongoDB Compass or CLI, connect to `mongodb://localhost:27017/`


### Release version will use a MongoDB Atlas Cluster.


### Test it ###

Run `python taskapp.py`

or `source dev.sh && python taskapp.py`

Open `http://127.0.0.1:5000/` on a browser to open the app
