import json
import random
from datetime import datetime

from flask import Flask, render_template, request, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import MySQLdb.cursors

APP_NAME = "ExePlore"
VERSION = "0.3-beta"

app = Flask(__name__)

app.secret_key = 'your secret key'

Bootstrap(app)
mysql = MySQL()
mysql.init_app(app)

bcrypt = Bcrypt()

with open('app/db/cards.json', 'r') as f:
    cards_dict = json.load(f)


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
        return render_template("index.html", APP_NAME=APP_NAME, VERSION=VERSION)

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

@app.route('/cards', methods=["GET"])
def cards():
    if 'loggedin' in session:
        return render_template('cards.html', APP_NAME=APP_NAME, VERSION=VERSION,
                               cards=cards_dict, won_cards=get_won_cards(session['username']))

    return redirect(url_for('login')), 401

@app.route('/card/<location>', methods=["GET"])
def single_card(location):
    if 'loggedin' in session:

        card = next(item for item in cards_dict if item["location"] == location)
        return render_template('current_card_page.html', APP_NAME=APP_NAME, VERSION=VERSION,
                               location=card['location'],
                               image=card['image'],
                               question=card['question'],
                               answers=card['answers'],
                               correctAnswer=card['correctAnswer'])

    return redirect(url_for('login')), 401

@app.route('/scores', methods=['GET', 'POST'])
def scores():
    if 'loggedin' in session:
        return render_template('scores.html', APP_NAME=APP_NAME, VERSION=VERSION)

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
        return render_template("admin_index.html", APP_NAME=APP_NAME, VERSION=VERSION)

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

#  Aux functions -------------------------------------------------------------------------------------------------------

def successful_login(username, password, gdpr_consent = None):
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

def get_won_cards(username):
    """
    Get locations of completed cards by session user
    :return: list of locations. [] if nothing found
    """
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # If command fails, don't bother with the rest. Clearly no username %s match
    if cursor.execute('SELECT cardLocation FROM won WHERE username = %s', (username,)):
        # Fetch one record and return result
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
        cursor.execute('INSERT INTO won (username, cardLocation, timeStamp) VALUES (%s, %s, %s)', (username, location, timestamp))
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
        cursor.execute('DELETE FROM won WHERE username=%s', (username, ))
    except:
        return False

    mysql.connection.commit()
    return True