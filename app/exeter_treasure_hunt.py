import csv
import json
import MySQLdb.cursors
from datetime import datetime

from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_mail import Mail, Message
from flask_debugtoolbar import DebugToolbarExtension

APP_NAME = "ExePlore"
VERSION = "0.3-beta"

app = Flask(__name__)

app.secret_key = 'your secret key'
app.debug= True

# Mail stuff
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="info@exeter.me",
    SECURITY_EMAIL_SENDER="info@exeter.me",
    MAIL_PASSWORD="1xtb7lfmuzss1y6kvuhz749r"
)

mail = Mail(app);

toolbar = DebugToolbarExtension(app)
# Consider disabling this in production. Should do it automatically but never know 😕


Bootstrap(app)
mysql = MySQL()
mysql.init_app(app)

bcrypt = Bcrypt()


class Config(object):
    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()
app.config.from_object(Config())

# it is also possible to enable the API directly
# scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

with open('app/db/cards.json', 'r') as f:
    cards_dict = json.load(f)


# Tasks ----------------------------------------------------------------------------------------------------------------

@scheduler.task('interval', id='do_save_progress', seconds=3600, misfire_grace_time=5)
def do_save_progress_job():
    with app.app_context():
        progress = get_overall_progress()
        with open("app/db/progress.csv", 'a') as f:
            f.write(str(progress) + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')


# Static pages ---------------------------------------------------------------------------------------------------------

@app.route('/landing-page', methods=['GET', 'POST'])
def landing_page():
    return render_template('landing_page.html', APP_NAME=APP_NAME, VERSION=VERSION)


@app.route('/gdpr-policy', methods=['GET', 'POST'])
def gdpr_policy():
    return render_template('gdpr_policy.html', APP_NAME=APP_NAME, VERSION=VERSION)


# Player auth section --------------------------------------------------------------------------------------------------

@app.route('/', methods=['GET'])
def index():
    if 'loggedin' in session:
        return render_template("index.html", APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'])

    return redirect(url_for('landing_page'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and \
            'username' in request.form and \
            'password' in request.form and \
            'consent' in request.form:

        msg = successful_login(request.form['username'], request.form['password'], request.form['consent'])
        if msg is None:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', APP_NAME=APP_NAME, VERSION=VERSION, msg=msg)

    return render_template('login.html', APP_NAME=APP_NAME, VERSION=VERSION)


@app.route('/card/<location>', methods=["GET"])
def single_card(location):
    if 'loggedin' in session:
        card = next(item for item in cards_dict if item["location"] == location)
        return render_template('current_card_page.html', APP_NAME=APP_NAME, VERSION=VERSION,
                               username=session['username'],
                               location=card['location'],
                               image=card['image'],
                               question=card['question'],
                               answers=card['answers'],
                               correctAnswer=card['correctAnswer'])

    return redirect(url_for('login')), 401


@app.route('/is-answer-correct', methods=["POST"])
def is_answer_correct():
    if 'loggedin' in session:
        location = request.form['location']
        answer = request.form['answer']

        card = next(item for item in cards_dict if item["location"] == location)

        if card["correctAnswer"] == answer:
            if not add_won_card(session['username'], location):
                return "Already completed card"
            return "Correct"
        else:
            return "Incorrect"

    return redirect(url_for('login')), 401


@app.route('/reset')
def reset():
    reset_my_cards(session['username'])

    # Redirect to login page
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('landing_page'))


# AJAX -------------------------------------------------------------------------

@app.route('/scores')
def scores():
    if 'loggedin' in session:        
        return render_template('scores.html', APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'])

    return redirect(url_for('login')), 401

@app.route('/map')
def map():
    if 'loggedin' in session:        
        return render_template('map.html', APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'])

    return redirect(url_for('login')), 401

@app.route('/cards')
def cards():
    if 'loggedin' in session:        
        return render_template('cards.html', APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'],
                               cards=cards_dict, won_cards=get_won_cards_by_user(session['username']))

    return redirect(url_for('login')), 401

# Admin section --------------------------------------------------------------------------------------------------------

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST' and \
            'username' in request.form and \
            'password' in request.form and \
            request.form['username'] == "admin":

        msg = successful_login(request.form['username'], request.form['password'])

        if msg is None:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = "admin"
            return redirect(url_for('admin_index'))
        else:
            return render_template('admin_login.html', APP_NAME=APP_NAME, VERSION=VERSION,
                                   msg=msg)

    return render_template('admin_login.html', APP_NAME=APP_NAME, VERSION=VERSION)


@app.route('/admin-index', methods=['GET'])
def admin_index():
    if 'loggedin' in session and session['username'] == "admin":
        won_cards = get_all_won_cards()
        users = get_all_users()

        return render_template("admin_index.html", APP_NAME=APP_NAME, VERSION=VERSION,
                               cards_dict=cards_dict,
                               num_won_cards=len(won_cards),
                               num_users=len(users),
                               num_active_users=get_num_of_active_players(),
                               overall_progress=round(get_overall_progress(), 2),
                               overall_progress_over_time=get_overall_progress_over_time(),
                               won_card_distribution=won_card_distribution(),
                               top_locations_by_playerbase_ownership=top_locations_by_playerbase_ownership())

    return redirect(url_for('admin_login')), 401


@app.route('/admin-map', methods=['GET'])
def admin_map():
    if 'loggedin' in session and session['username'] == "admin":
        return render_template("map_view.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return redirect(url_for('admin_login')), 401


@app.route('/admin-users', methods=['GET'])
def admin_users():
    if 'loggedin' in session and session['username'] == "admin":
        return render_template("user_list.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return redirect(url_for('admin_login')), 401


# Mail stuff ------------------------------------------------------------------

@app.route('/testMail', methods=['GET'])
def testMail():
    msg = mail.send_message(
        subject='Anthony Test Mail Thingy',
        sender="info@exeter.me",
        recipients=["arb239@exeter.ac.uk"],
        html="Congratulations Anthony! You have sent an email from our Flask server."
    )
    return "<h1>Sent mail</h1>"

#  Aux functions -------------------------------------------------------------------------------------------------------

def successful_login(username, password, gdpr_consent=None):
    """
    Can user login

    :param username: username string
    :param password: plain text password
    :param gdpr_consent: "concent" or anything else
    :return: None if successful else a message
    """

    # For reference: https://codeshack.io/login-system-python-flask-mysql/
    if gdpr_consent != 'consent' and gdpr_consent != None:
        msg = "Check GDPR consent to continue"
        return msg

    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # If command fails, don't bother with the rest. Clearly no username %s match
    if cursor.execute('SELECT password FROM users WHERE username = %s', (username,)):
        # Fetch one record and return result
        password_hash = cursor.fetchone()['password']
    else:
        msg = "User account does not exist"
        return msg

    authenticated_user = bcrypt.check_password_hash(password_hash, password)
    if authenticated_user:
        # Redirect to home page
        return None
    else:
        # Account doesnt exist or username/password incorrect
        msg = 'Incorrect username/password!'
        return msg


def get_all_users():
    """
    Get all users
    :return: list of users. [] if nothing found
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # If command fails, don't bother with the rest. Clearly no username %s match
    if cursor.execute('SELECT * FROM users'):
        # Fetch one record and return result
        users = cursor.fetchall()
        return users
    else:
        return []


def get_num_of_active_players():
    """
    Get number of players that have won a card
    :return: int
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # If command fails, don't bother with the rest. Clearly no username %s match
    if cursor.execute('SELECT COUNT(username) FROM won'):
        # Fetch one record and return result
        num_users = cursor.fetchall()
        return num_users[0]['COUNT(username)']
    else:
        return 0


def get_all_won_cards():
    """
    Get completed cards
    :return: list of cards. [] if nothing found
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # If command fails, don't bother with the rest. Clearly no username %s match
    if cursor.execute('SELECT * FROM won'):
        # Fetch one record and return result
        wons = cursor.fetchall()
        return wons
    else:
        return []


def get_overall_progress():
    """
    Get overall progress
    :return: num between 0 and 100%
    """

    won_cards = get_all_won_cards()
    users = get_all_users()

    return (len(won_cards) * 100) / (len(users) * len(cards_dict))


def get_overall_progress_over_time():
    """
    Get overall progress over time.
    :return: list of tuples. (progress score, timestamp)
    """
    progress = [tuple(row) for row in csv.reader(open("app/db/progress.csv", 'rU'))]

    return progress


def won_card_distribution():
    """
    Get num of won cards by location
    :return: list of cardLocation, COUNT(*)
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if cursor.execute('SELECT cardLocation, COUNT(*) FROM won GROUP BY cardLocation'):
        distribution = list(cursor.fetchall())
        return distribution
    else:
        return []


def top_locations_by_playerbase_ownership():
    """
    Get location by completeness of users
    :return: dict. location : %
    """

    won_cards = won_card_distribution()
    percentage_complete = {}
    for card in won_cards:
        percentage_complete[card['cardLocation']] = (card['COUNT(*)'] * 100) / len(get_all_users())

    return sorted(percentage_complete.items(), key=lambda x: x[1], reverse=True)


def get_won_cards_by_user(username):
    """
    Get locations of completed cards by session user
    :return: list of locations. [] if nothing found
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if cursor.execute('SELECT cardLocation FROM won WHERE username = %s', (username,)):
        locations = [item['cardLocation'] for item in cursor.fetchall()]
        return locations
    else:
        return []


def add_won_card(username, location):
    """
    Add completed card entry to won db

    :param username: string
    :param location: string card location
    :return: True if successful, else false
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        cursor.execute('INSERT INTO won (username, cardLocation, timeStamp) VALUES (%s, %s, %s)',
                       (username, location, timestamp))
    except:
        return False

    mysql.connection.commit()
    return True


def reset_my_cards(username):
    """
    Removes completed cards from won db

    :param username: string
    :return: True if successful, else false
    """

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute('DELETE FROM won WHERE username=%s', (username,))
    except:
        return False

    mysql.connection.commit()
    return True
