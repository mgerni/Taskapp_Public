
=======
Taskapp

## Initial Setup ###

### Install latest Python 3 version ###
`https://www.python.org/downloads/`

### Create a virtualenv ###
`python3 -m venv /path/`

### Activate virtualenv ###
`source /path/bin/activate`

### Clone master branch ###
The master branch has changes suitable for devolpment, which includes using a local database. 

### Install dependencies ###
`pip install -r requirements.txt`

### MongoDB Setup - Local Testing ###
Follow instructions on `https://docs.mongodb.com/manual/administration/install-community/` to install mongoDB

In mongoDB Compass or CLI, connect to `mongodb://localhost:27017/`


### Release version will use a MongoDB Atlas Cluster. 


### Test it ###

Run `python taskapp.py`

Open `http://127.0.0.1:5000/` on a browser to open the app

