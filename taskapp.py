from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify, make_response
from flask_recaptcha import ReCaptcha
import jwt
import datetime
import bcrypt
import config
from functools import wraps
import task_login
import tasklists
from task_database import (get_taskCurrent, generate_task, complete_task, get_task_progress,
                           get_task_lists, manual_complete_tasks, manual_revert_tasks,
                           import_spreadsheet, uncomplete_all_tasks, lms_status_change,
                           official_status_change, username_change, official_icon, unofficial_icon, get_taskCurrent_tier, generate_task_for_tier,
                           complete_task_unofficial_tier, get_user, get_leaderboard)
import send_grid_email
from rank_check import get_collection_log, check_collection_log

app = Flask(__name__)

isProd = config.IS_PROD

# Set secret key for Flask App.
app.config['SECRET_KEY'] = config.SECRET_KEY

if isProd:
    # Keys for Google reCAPTCHA.
    app.config['RECAPTCHA_SITE_KEY'] = config.SECRET_KEY
    app.config['RECAPTCHA_SECRET_KEY'] = config.SECRET_KEY
    # initialize reCAPTCHA
    recaptcha = ReCaptcha(app)
else:
    recaptcha = "Disabled for DEV"


# email service account.
taskapp_email = config.SECRET_KEY

# specifies database to use.
db = config.MONGO_CLIENT["TaskAppLoginDB"]


'''
before_request function:

The before_request function is run before every request to force HTTPS protocol. 

Args:
    None
Returns:
    redirect_url str: of https://www.osrstaskapp.com
    code int: of 301


'''
if isProd:
    @app.before_request
    def before_request():
        if not request.is_secure:
            current_url = request.url
            if current_url.startswith('http://'):
                redirect_url = current_url.replace('http://', 'https://', 1)
            elif current_url.startswith('www'):
                redirect_url = current_url.replace('www', 'https://www', 1)
            else:
                redirect_url = 'https://www.osrstaskapp.com'
            code = 301
            return redirect(redirect_url, code=code)



'''
login_required function:

The login_requried function is used to ensure that only logged in users can access certain pages.

Args:
    Wrap(*args, **kwargs):
Returns:
    redirect request: to login page if the user is not logged in. 


'''
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You must be logged in to access this page!")
            return redirect(url_for('login'))
    return wrap


class APIUser:
    def __init__(self, username):
        self.username = username


'''
Class to hold data that is used in many templates
'''
class BasePageInfo:
    def __init__(self):
        username = session['username']
        user = get_user(username)
        self.username = username
        self.user = user
        self.official = user.is_official
        progress = get_task_progress(username)
        self.progress = progress
        if self.official:
            self.rank_icon = official_icon(progress[0], progress[1], progress[2], progress[3])
        else:
            self.rank_icon = unofficial_icon(username)
        email_verify = task_login.email_verify(username)
        self.email_bool = email_verify[0]
        self.email_val = email_verify[1]


# Converts dict from users task data to a list of user data represented as another list.
# Also filters out LMS fields
# Going forward, convert pages to use the class above instead
def filter_lms(t_list):
    items = []
    for item in t_list:
        for x in item['taskname'].items():
            if 'LMS' not in x:
                tip = item.get('taskTip')
                newItemAsList = [x[0], x[1], item['status'], item['_id'],item['taskCurrent'],]
                if tip is not None:
                    newItemAsList.append(tip)
                newItemAsList.append(item['wikiLink'])
                items.append(newItemAsList)
    return items


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'a valid token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = APIUser(data['username'])

        except:
            return jsonify({'message': 'Token is invalid'}), 403
        return f(user, *args, **kwargs)
    return decorated

@app.route('/api/v1/resource/login')
def api_login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response({'message': 'Could not verify'}, 401, {'WWW.Authentication': 'Basic realm: "login required"'})
    coll = db['users']
    user = coll.find_one({'username': auth.username}, {'_id': 0})
    if not user:
        return make_response('Could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    if bcrypt.checkpw(auth.password.encode('utf-8'), user['hashed_password']):
        token = jwt.encode({'username': user['username'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)}, app.config['SECRET_KEY'])
        return jsonify({'token': token}), 200

    return make_response({'message': 'Could not verify'}, 401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/api/v1/resource/current_task')
@token_required
def api_current_task(user):
    current_task = get_taskCurrent(user.username)
    if current_task:
        return jsonify({'message': {'taskName': current_task[0], 'taskImage': current_task[6]}})
    return jsonify({'message': None})

@app.route('/api/v1/resource/task_progress')
@token_required
def api_task_progress(user):
    progress = get_task_progress(user.username)
    return jsonify({'message':
    {
        'easy_progress': progress[0],
        'easy_complete': progress[4],
        'easy_total': progress[5],
        'medium_progress': progress[1],
        'medium_complete': progress[6],
        'medium_total': progress[7],
        'hard_progress': progress[2],
        'hard_complete': progress[8],
        'hard_total': progress[9],
        'elite_progress': progress[3],
        'elite_complete': progress[10],
        'elite_total': progress[11]
    }})


@app.route('/api/v1/resource/generate_task')
@token_required
def api_generate_task(user):
    current_task = get_taskCurrent(user.username)
    if current_task:
        return jsonify({'message': 'User already has a task'})

    generate_task(user.username)
    current_task = get_taskCurrent(user.username)
    if current_task:
        return jsonify({'message': {'taskName': current_task[0], 'taskImage' : current_task[6]}})
    return jsonify({'message': 'No available tasks to generate!'})

@app.route('/api/v1/resource/complete_task')
@token_required
def api_complete_task(user):
    current_task = get_taskCurrent(user.username)
    if current_task:
        complete_task(user.username)
        return jsonify({'message': 'Success'})
    return jsonify({'message': 'User does not have a task'})

'''
All @app.route functions:

The @app.route functions are used to route the user to the correct page.
@app.route functions render an HTML template and pass in variables to the template. 
Many @app.route functions call functions from task_login.py and/or task_database.py
Functions will be explained in more detail in the functions themselves.
'''



# Base route for the website, renders welcome.html
@app.route('/')
def index():
    return render_template('welcome.html')

# Register route, renders register.html on GET request.
# On POST request, verifies the users input and creates a new user in the database.
@app.route('/register/', methods=['GET', 'POST'])
def register():
    try:
        error = None
        if request.method == 'POST':
            if (not isProd) or recaptcha.verify():
                form_data = request.form
                username = form_data['username']
                password = form_data['password']
                repeat_password = form_data['repeat_password']
                email = form_data['email']
                is_official = request.form.get('officialstatus') == 'on'
                lms_status = request.form.get('lmsstatus') is None
                if password != repeat_password:
                    error = 'Passwords did not match. Please Try again. '
                    return render_template('register.html', error=error)
                else:

                    create_user = task_login.add_user(username, password, email, is_official, lms_status)
                    if create_user[0] == True:
                        send_verification_email_inital(email, username)
                        flash('Account %s Created Successfully!' % username)
                        flash('Verification email was sent to %s, please check your email (be sure to check your spam folder).' % email)
                        return redirect('/login/')
                    else:
                        error = create_user[1]
                        return render_template('register.html', error=error)
            else:
                error = 'Please fill out the Captcha!'
                return render_template('register.html', error=error)
        else:
            return render_template('register.html', error=error)
    except Exception as e:
        app.logger.error('Error', e)
        error = 'An error occurred while processing your request, please try again.'
        return render_template('register.html', error=error)


# Login route, renders login.html on GET request.
# On POST request, verifies the users input and logs the user in.
@app.route('/login/', methods= ['GET', 'POST'])
def login():
    try:
        error = None
        coll = db['users']
        if request.method == 'POST':
            if (not isProd) or recaptcha.verify():
                form_data = request.form
                attempted_username = form_data['username']
                attempted_password = form_data['password']
                username_found = coll.find_one({"username": attempted_username})
                if username_found:
                    passwordcheck = username_found['hashed_password']
                    if bcrypt.checkpw(attempted_password.encode('utf-8'), passwordcheck):
                        session['logged_in'] = True
                        session['username'] = request.form['username']
                        return redirect(url_for('dashboard'))
                    else:
                        error = "Invalid Username or Password. Please Try again"
                        return render_template('login.html', error=error)
                else:
                    error = "Invalid Username or Password. Please Try again"
                    return render_template('login.html', error=error)
            else:
                error = 'Please fill out the Captcha!'
                return render_template('login.html', error=error)
        else:
            return render_template('login.html', error=error)
    except Exception as e:
        error = "An error occurred while processing your request, please try again."
        return render_template('login.html', error=error)


# logout route, logs the user out and redirects to the login page.
@app.route('/logout/')
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for('login'))

# dashboard route, renders index.html or dashboard_unofficial.html depending on the user's status (official or unofficial) on GET request.
# I don't remember why POST is specified here, but it works.
@app.route('/dashboard/', methods=['GET', 'POST'])
@login_required
def dashboard():
    user_info = BasePageInfo()
    # The "first" variables determine whether a user has just completed a task
    easy_first = bool(request.args.get('easy-first'))
    medium_first = bool(request.args.get('medium-first'))
    hard_first = bool(request.args.get('medium-first'))
    elite_first = bool(request.args.get('medium-first'))
    username = session['username']
    progress = get_task_progress(username)
    context = {
        'username': username,
        'rank_icon': user_info.rank_icon,
        'email_verify': user_info.email_bool,
        'email_val': user_info.email_val,
        'official': user_info.official,
        'taskapp_email': taskapp_email,
        'easy': progress[0],
        'medium': progress[1],
        'hard': progress[2],
        'elite': progress[3]
    }
    if user_info.official:
        current_task = get_taskCurrent(username)
        print(current_task)
        if current_task:
            task, image, _, _, tip, link, _ = current_task
            context.update({
                'task': task,
                'image': image,
                'tip': tip,
                'link': link
            })
            return render_template('index.html', **context)

        else:
            context.update({
                'task': '',
                'image': None,
                'tip': None,
                'link': None,
                'easy_first': easy_first,
                'medium_first': medium_first,
                'hard_first': hard_first,
                'elite_first': elite_first

            })
            return render_template('index.html', **context)
    else:
        context['easy_progress'], context['medium_progress'], context['hard_progress'], context['elite_progress'] = progress[0], progress[1], progress[2], progress[3]
        for tier, task_type in [('easy', 'easyTasks'), ('medium', 'mediumTasks'), ('hard', 'hardTasks'), ('elite', 'eliteTasks')]:
            current_task = get_taskCurrent_tier(username, task_type)
            if current_task:
                context[f'task_{tier}'], context[f'image_{tier}'], _, _, context[f'tip_{tier}'], context[f'link_{tier}'], _ = current_task
            else:
                context.update({
                    f'task_{tier}': '',
                    f'image_{tier}': None,
                    f'tip_{tier}': None,
                    f'link_{tier}': None
                })
        return render_template('dashboard_unofficial.html', **context)

# AJAX route for importing a exisiting Generate Task Spreadsheet.
@app.route('/import/', methods=['POST'])
@login_required
def import_dashboard():
    try:
        form_data = request.form
        username = session['username']
        url = form_data['spreadsheet_url']
        uncomplete_all_tasks(username)
        import_data = import_spreadsheet(username, url)
        import_task_logs = import_data[0]
        import_current_logs = import_data[1]
        error = import_data[2]
        if len(import_task_logs) != 0:
            for task_logs in import_task_logs:
                flash(task_logs)
        if len(import_current_logs) != 0:
            for current_logs in import_current_logs:
                flash(current_logs)
        if error is not None:
            flash(error)
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(str(e))
        error = "There was an error proccessing the request, contact Gerni Task on Discord"
        flash(error)
        return redirect(url_for('dashboard'))



# AJAX route for exporting Task App progress to a shareable spreadsheet.
# @app.route('/export_progress/', methods=['POST'])
# @login_required
# def export_progress():
#     username = session['username']
#     email_address = task_login.query_email(username)
#     progress = get_task_progress(username)
#     easy_progress, medium_progress, hard_progress, elite_progress = progress[0], progress[1], progress[2], progress[3]
#     task_lists = get_task_lists(username)
#     easy_list, medium_list, hard_list, elite_list, bosspet_list, skillpet_list, otherpet_list, extra_list, passive_list = (
#         task_lists[0],
#         task_lists[1],
#         task_lists[2],
#         task_lists[3],
#         task_lists[4],
#         task_lists[5],
#         task_lists[6],
#         task_lists[7],
#         task_lists[8])
#     lms_status = lms_check(username)
#     generate_sheet = copy_master_sheet(username)
#     if generate_sheet[0] is False:
#         error = 'An error occured while generating the spreadsheet. Please try again in a few minutes. This is likely due to Google API rate limiting.'
#         return render_template('export_progress_error.html', error=error)
#     else:
#         google_sheet = update_spreadsheet(
#             username,
#             email_address,
#             generate_sheet[1],
#             easy_progress,
#             medium_progress,
#             hard_progress,
#             elite_progress,
#             easy_list,
#             medium_list,
#             hard_list,
#             elite_list,
#             bosspet_list,
#             skillpet_list,
#             otherpet_list,
#             extra_list,
#             passive_list,
#             lms_status)
#         if google_sheet[0] is False:
#             return render_template('export_progress_error.html', error=google_sheet[0])
#         else:
#             return render_template('export_progress.html', google_sheet=google_sheet[1])

@app.route('/collectionlog_check/', methods=['POST'])
@login_required
def collection_log_check():
    form_data = request.form
    rs_username = form_data['username']
    log_data = get_collection_log(rs_username)
    if log_data[0] == 200:
        easy_check = check_collection_log(tasklists.easy, log_data[1])
        medium_check = check_collection_log(tasklists.medium, log_data[1])
        hard_check = check_collection_log(tasklists.hard, log_data[1])

        return render_template('collection_log_check.html',
        rs_username = rs_username,
        easy_check= easy_check,
        medium_check= medium_check,
        hard_check = hard_check
        )
    else:
        print(log_data[0], log_data[1]['error'])
        return render_template('collection_log_check_error.html', rs_username=rs_username, error=log_data[1]['error'])

# Form request route for generating a task for official users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/generate/', methods=['POST'])
@login_required
def generate_button():
    username = session['username']
    generate_task(username)
    return redirect(url_for('dashboard'))


# Form request route for generating a easy task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/generate_unofficial_easy/', methods=['POST'])
@login_required
def generate_unofficial_easy():
    username = session['username']
    generate_task_for_tier(username, 'easyTasks')
    return redirect(url_for('dashboard'))

# Form request route for generating a medium task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/generate_unofficial_medium/', methods=['POST'])
@login_required
def generate_unofficial_medium():
    username = session['username']
    generate_task_for_tier(username, 'mediumTasks')
    return redirect(url_for('dashboard'))

# Form request route for generating a hard task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/generate_unofficial_hard/', methods=['POST'])
@login_required
def generate_unofficial_hard():
    username = session['username']
    generate_task_for_tier(username, 'hardTasks')
    return redirect(url_for('dashboard'))

# Form request route for generating a elite task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/generate_unofficial_elite/', methods=['POST'])
@login_required
def generate_unofficial_elite():
    username = session['username']
    generate_task_for_tier(username, 'eliteTasks')
    return redirect(url_for('dashboard'))


# Form request route for completing a task for official users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/complete/', methods =['POST'])
@login_required
def complete_button():
    username = session['username']
    current_task = get_taskCurrent(username)
    if current_task is not None:
        query_params = complete_task(username)
        return redirect(url_for('dashboard', **query_params))
    return redirect(url_for('dashboard'))



# Form request route for completing a easy task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/complete_unofficial_easy/', methods =['POST'])
@login_required
def complete_unofficial_easy():
    username = session['username']
    current_task = get_taskCurrent_tier(username, 'easyTasks')
    if current_task is not None:
        task_id = current_task[3]
        query_params = complete_task_unofficial_tier(username, task_id, 'easyTasks')
        return redirect(url_for('dashboard'), **query_params)
    return redirect(url_for('dashboard'))


# Form request route for completing a medium task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/complete_unofficial_medium/', methods =['POST'])
@login_required
def complete_unofficial_medium():
    username = session['username']
    current_task = get_taskCurrent_tier(username, 'mediumTasks')
    if current_task is not None:
        task_id = current_task[3]
        query_params = complete_task_unofficial_tier(username, task_id, 'mediumTasks')
        return redirect(url_for('dashboard'), **query_params)
    return redirect(url_for('dashboard'))


# Form request route for completing a hard task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/complete_unofficial_hard/', methods =['POST'])
@login_required
def complete_unofficial_hard():
    username = session['username']
    current_task = get_taskCurrent_tier(username, 'hardTasks')
    if current_task is not None:
        task_id = current_task[3]
        query_params = complete_task_unofficial_tier(username, task_id, 'hardTasks')
        return redirect(url_for('dashboard'), **query_params)
    return redirect(url_for('dashboard'))


# Form request route for completing a elite task for unofficial users.
# The Form request/action method was used before I started using AJAX.
# Should be modified to use AJAX eventually.
@app.route('/complete_unofficial_elite/', methods =['POST'])
@login_required
def complete_unofficial_elite():
    username = session['username']
    current_task = get_taskCurrent_tier(username, 'eliteTasks')
    if current_task is not None:
        task_id = current_task[3]
        query_params = complete_task_unofficial_tier(username, task_id, 'eliteTasks')
        return redirect(url_for('dashboard'), **query_params)
    return redirect(url_for('dashboard'))


# route for task-list page, this page lists all tasks easy, medium, hard, elite, extra, passive and pets.
@app.route('/task-list/', methods=['GET'])
@login_required
def task_list():
    user_info = BasePageInfo()

    task = get_task_lists(user_info.username)

    # TODO Refactor template to use the user page_tasks class
    items_easy = filter_lms(task[0])
    items_medium = filter_lms(task[1])
    items_hard = filter_lms(task[2])
    items_elite = filter_lms(task[3])
    items_bosspet = filter_lms(task[4])
    items_skillpet = filter_lms(task[5])
    items_otherpet = filter_lms(task[6])
    items_extra = filter_lms(task[7])
    items_passive = filter_lms(task[8])

    return render_template(
        'task_list.html',
        username=user_info.username,
        email_verify=user_info.email_bool,
        rank_icon=user_info.rank_icon,
        email_val=user_info.email_val,
        items_easy=items_easy,
        items_medium=items_medium,
        items_hard=items_hard,
        items_elite=items_elite,
        items_bosspet=items_bosspet,
        items_skillpet=items_skillpet,
        items_otherpet=items_otherpet,
        items_extra=items_extra,
        items_passive=items_passive,
        taskapp_email=taskapp_email,
        official=user_info.official
        )

def single_task_list(list_title, task_type):
    user_info = BasePageInfo()
    items = user_info.user.page_tasks(task_type)
    return render_template(
        'single-task-list.html',
        list_title=list_title,
        task_type=task_type,  # Needed as it is ingrained in JS for updating tasks
        username=user_info.username,
        email_verify=user_info.email_bool,
        rank_icon=user_info.rank_icon,
        email_val=user_info.email_val,
        items=items,
        taskapp_email=taskapp_email,
        official=user_info.official
    )

# route for task-list-easy, only shows easy tasks.
@app.route('/task-list-easy/', methods=['GET'])
@login_required
def task_list_easy():
    return single_task_list(list_title='Easy Task List', task_type='easy')

#route for task-list-medium, only shows medium tasks.
@app.route('/task-list-medium/', methods=['GET'])
@login_required
def task_list_medium():
    return single_task_list(list_title='Medium Task List', task_type='medium')

# route for the hard task list, only shows hard tasks.
@app.route('/task-list-hard/', methods=['GET'])
@login_required
def task_list_hard():
    return single_task_list(list_title='Hard Task List', task_type='hard')


# route for the elite task list, only shows elite tasks.
@app.route('/task-list-elite/', methods=['GET'])
@login_required
def task_list_elite():
    return single_task_list(list_title='Elite Task List', task_type='elite')

# route for the pets task list, only shows pets tasks.
@app.route('/task-list-pets/', methods=['GET'])
@login_required
def task_list_pets():
    user_info = BasePageInfo()
    task = get_task_lists(user_info.username)
    items_bosspet = filter_lms(task[4])
    items_skillpet = filter_lms(task[5])
    items_otherpet = filter_lms(task[6])

    return render_template(
        'task-list-pets-new.html',
        username=user_info.username,
        email_verify=user_info.email_bool,
        rank_icon=user_info.rank_icon,
        email_val=user_info.email_val,
        items_bosspet=items_bosspet,
        items_skillpet=items_skillpet,
        items_otherpet=items_otherpet,
        taskapp_email=taskapp_email,
        official=user_info.official
        )

# route for extra task list, only shows extra tasks.
@app.route('/task-list-extra/', methods=['GET'])
@login_required
def task_list_extra():
    return single_task_list(list_title='Extra Task List', task_type='extra')

# route for passive task list, only shows passive tasks.
@app.route('/task-list-passive/', methods=['GET'])
@login_required
def task_list_passive():
    return single_task_list(list_title='Passive Task List', task_type='passive')

@app.route('/hiscores', methods=['GET'])
@login_required
def highscores():
    user_info = BasePageInfo()
    return render_template(
        'highscores.html',
        username=user_info.username,
        email_verify=user_info.email_bool,
        rank_icon=user_info.rank_icon,
        email_val=user_info.email_val,
        taskapp_email=taskapp_email,
        official=user_info.official,
        leaderboard=get_leaderboard()
    )

tier_to_type = {
    "easyTasks": 'easy',
    "mediumTasks": 'medium',
    "hardTasks": 'hard',
    "eliteTasks": 'elite',
    "bossPetTasks": 'pet',
    "skillPetTasks": 'pet',
    "otherPetTasks": 'pet',
    "passiveTasks": 'passive',
    "extraTasks": 'extra',
}

# AJAX route for completing tasks manually on task-list page(s).
# only returns HTML specific to the task.
# Javascript used to change the HTML that is displayed.
@app.route('/update_completed/', methods= ['POST'])
@login_required
def update():

    task_id = request.form['id']
    tier = request.form['name']
    task_update = manual_complete_tasks(session['username'], tier, task_id)
    task = task_update[0]
    image = task_update[1]
    tip = task_update[2]
    link = task_update[3]

    task_type = tier_to_type[tier]
    return render_template('update_completed_easy.html', task=task, image=image, task_id=task_id, tier=tier, task_type=task_type, tip=tip, link=link)


# AJAX route for uncompleting/reverting tasks manually on task-list page(s).
# only returns HTML specific to the task.
# Javascript used to change the HTML that is displayed.
@app.route('/revert_completed/', methods = ['POST'])
@login_required
def revert():
    task_id = request.form['id']
    tier = request.form['name']
    task_revert = manual_revert_tasks(session['username'], tier, task_id)
    task = task_revert[0]
    image = task_revert[1]
    tip = task_revert[2]
    link = task_revert[3]
    task_type = tier_to_type[tier]
    return render_template('revert_completed_easy.html', task=task, image=image, task_id=task_id, tier=tier, task_type=task_type, tip=tip, link=link)



# route for FAQ page.
@app.route('/faq/')
@login_required
def faq():
    user_info = BasePageInfo()
    return render_template(
        'faq.html',
        username=user_info.username,
        email_verify=user_info.email_bool,
        email_val=user_info.email_val,
        rank_icon=user_info.rank_icon,
        taskapp_email=taskapp_email
        )

#route for Wall-of-pain page.
@app.route('/wall-of-pain/')
@login_required
def wall_of_pain():
    user_info = BasePageInfo()
    return render_template(
        'wall_of_pain.html',
        username=user_info.username,
        email_verify=user_info.email_bool,
        email_val=user_info.email_val,
        rank_icon=user_info.rank_icon,
        taskapp_email=taskapp_email
    )



# Function to send email using send_grid API.
def send_reset_email(email, username):
    token = task_login.get_reset_token(username)
    email_message = send_grid_email.send_message(
    email,
    'Password Reset Request For Task App',
    f'''To reset your password, visit the following link:
    {url_for('reset_token', token=token, _external=True)}

    Thank you for using Task App

    If you did not make this request simply ignore this email. 
    '''
    )

# Function to send email using send_grid API.
def send_verification_email(email, username):
    token = task_login.get_email_verify_token(username, email)
    email_message = send_grid_email.send_message(
        email,
    'Email verification for OSRS Task App',
    f'''To verify your account, visit the following link:
    {url_for('email_verify', token=token, _external=True)}

    Thank you for using Task App
    ''')

# Function to send email using send_grid API.
def send_verification_email_inital(email, username):
    token = task_login.get_email_verify_token(username, email)
    email_message = send_grid_email.send_message(
        email,
    'Email verification for OSRS Task App',
    f'''To verify your account, visit the following link:
    {url_for('email_verify_inital', token=token, _external=True)}

    Thank you for using Task App
    ''')

# AJAX email verify route
@app.route('/email_verify/', methods=['POST'])
@login_required
def verify():
    email = request.form['email']
    username = session['username']
    send_verification_email(email, username)
    return render_template('email_modal.html')

# AJAX email verify requiring a token for email verification.
@app.route('/email_verify/<token>')
@login_required
def email_verify(token):
    user = task_login.verify_email_verify_token(token)
    if user is None:
        flash("That is an invalid or expired token")
        return redirect(url_for('dashboard'))
    task_login.update_email(user[0], user[1])
    flash("Thank you for verifying your email address!")
    return redirect(url_for('dashboard'))

# AJAX email verify requiring a token for email verification.
@app.route('/email_verify_inital/<token>')
def email_verify_inital(token):
    user = task_login.verify_email_verify_token(token)
    if user is None:
        flash("That is an invalid or expired token")
        return redirect(url_for('login'))
    task_login.update_email(user[0], user[1])
    flash("Thank you for verifying your email address!")
    return redirect(url_for('login'))


# Route for reset password page.
@app.route("/reset_password/", methods=['GET', 'POST'])
def reset_request():
    if request.method == 'GET':
        try:
            if session['username']:
                flash('You are already logged in.')
                return redirect(url_for('dashboard'))
        except KeyError:
            pass
        return render_template('reset_request.html')
    if request.method == 'POST':

        form_data = request.form
        email = form_data['email']
        email_query = task_login.query_email(email)
        if email_query is None:
            flash('Email address not found.', 'warning')
            return render_template('reset_request.html')
        username = email_query['username']
        send_reset_email(email, username)
        flash('Email sent to %s. Be sure to check your spam folder.' % email)
        return redirect(url_for('login'))

# route for password reset page requiring a token.
@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if request.method == 'GET':
        try:
            if session['username']:
                flash('You are already logged in.')
                return redirect(url_for('dashboard'))
        except KeyError:
            pass
        user = task_login.verify_reset_token(token)
        if user is None:
            flash('That is an invalid or expired token')
            return redirect(url_for('reset_request'))

        return render_template('reset_password.html')
    if request.method == 'POST':
        user = task_login.verify_reset_token(token)
        error = None
        form_data = request.form
        password = form_data['password']
        repeat_password = form_data['repeat_password']
        if password != repeat_password:
            error = 'Passwords did not match. Please Try again. '
            return render_template('reset_password.html', error=error)
        else:
            change_pass = task_login.change_password(user, password)
            if change_pass[0] == True:
                flash('Password changed sucessfully, please login.')
                return redirect(url_for('login'))
            else:
                error = change_pass[1]
                return render_template('reset_password.html', error=error)


# Route for profile page.
@app.route("/profile/")
def profile():
    user_info = BasePageInfo()

    return render_template(
        'profile.html',
        username=user_info.username,
        email_verify=user_info.email_bool,
        email_val=user_info.email_val,
        official=user_info.official,
        rank_icon=user_info.rank_icon,
        lms_status=user_info.user.lms_enabled)

# AJAX route for profile email change.
# I don't know why I didn't just change the HTML via javascript...
@app.route("/profile_emailChange/", methods=['POST'])
def emailChange():
    username = session['username']
    email_verify = task_login.email_verify(username)
    email_val = email_verify[1]
    return render_template('email_change.html', username=username, email_value=email_val)


# AJAX route for profile email change.
# This one is needed to actually change the email in the database.
@app.route("/profile_emailChangeSubmit/", methods=['POST'])
def emailChangeSubmit():
    email_val = request.form['email']
    username = session['username']
    task_login.email_change(username, email_val)
    return render_template('email_change_submit.html', email_val=email_val, username=username)

# AJAX route for profile username change.
# I don't know why I didn't just change the HTML via javascript...
@app.route("/profile_usernameChange/", methods=['POST'])
def usernameChange():
    print('POST RECIVED')
    username = session['username']
    email_verify = task_login.email_verify(username)
    email_val = email_verify[1]
    return render_template('username_change.html', email_val=email_val)


# AJAX route for profile username change.
# This one is needed to actually change the username in the database.
@app.route("/profile_usernameChangeSubmit/", methods=['POST'])
def usernameChangeSubmit():
    username_value = request.form['username']
    username = session['username']
    print(username)
    email_verify = task_login.email_verify(username)
    email_val = email_verify[1]

    if username == username_value:
        error = "%s is already your username..." % username_value
        return render_template('username_change_submit.html', username=username, email_val=email_val, error=error)
    else:
        change_username_result = task_login.username_change(username, username_value)
        change_username_result_taskaccount = username_change(username, username_value)

        if change_username_result and change_username_result_taskaccount == True:
            session['username'] = username_value
            username = session['username']
            return render_template('username_change_submit.html', username=username, email_val=email_val)
        else:
            error = change_username_result
            return render_template('username_change_submit.html', username=username, change_username_result=change_username_result, error=error)

# AJAX route to change LMS status
@app.route("/change_lms_status/", methods=['POST'])
def change_lms_status():
    username = session['username']
    data = request.form['lms_status']
    if data == 'true':
        data = True
        lms_status_change(username, data)
    elif data == 'false':
        data = False
        lms_status_change(username, data)
    return render_template('lms_change.html')

# AJAX route to change offical status
@app.route("/profile_change_official/", methods=['POST'])
def change_official_status():
    username = session['username']
    data = request.form['official_status']
    if data == 'false':
        official_status_change(username)
    return redirect(url_for('profile'))

# AJAX route to change password
@app.route("/profile_passwordChangeSubmit/", methods=['POST'])
def change_password_profile():
    username = session['username']
    new_password = request.form['change_password']
    confirm_password = request.form['confirm_password']

    if new_password != '':
        if new_password == confirm_password:
            change_pass = task_login.change_password(username, new_password)
            success = change_pass[0]
            if not success:
                error = change_pass[1]
                return render_template('change_password_error.html', error=error)
            else:
                success = 'Password Changed!'
                return render_template('change_password_error.html', success=success)
        else:
            return render_template('change_password_error.html', error='Passwords do not match!')
    else:
        return render_template('change_password_error.html', error='Password fields are not filled out!')


# AJAX route for task-help.
@app.route("/task_help/", methods=['POST'])
def taskHelp():
    tip = request.form['tip']
    link = request.form['link']
    if tip != 'None':
        return render_template('task_help.html', tip=tip, link=link)
    else:
        tip = ''
        return render_template('task_help.html', tip=tip, link=link)


if __name__ == "__main__":
    if (isProd):
        app.run(host='0.0.0.0')
    else:
        app.run(host="0.0.0.0", port=5000)