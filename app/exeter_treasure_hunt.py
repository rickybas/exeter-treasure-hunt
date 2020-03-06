import json
import random

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


@app.route('/', methods=['GET'])
def index():
    if 'loggedin' in session:
        return render_template("index.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return redirect(url_for('landing_page'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    # For reference: https://codeshack.io/login-system-python-flask-mysql/
    msg = ''
    if request.method == 'POST' and \
            'username' in request.form and \
            'password' in request.form and \
            'consent' in request.form:
        username = request.form['username']
        password = request.form['password']
        gdpr_consent = request.form['consent']

        if gdpr_consent != 'consent':
            msg = "Check GDPR consent to continue"
            render_template('login.html', msg=msg)

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # If command fails, don't bother with the rest. Clearly no username %s match
        if cursor.execute('SELECT password FROM users WHERE username = %s', (username,)):
            # Fetch one record and return result
            password_hash = cursor.fetchone()['password']
        else:
            msg = "User account does not exist"
            return render_template('login.html', msg=msg)

        authenticated_user = bcrypt.check_password_hash(password_hash, password)
        if authenticated_user:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = username
            session['cards'] = cards_dict
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    return render_template('login.html', msg=msg)

@app.route('/cards', methods=["GET"])
def cards():
    if 'loggedin' in session:
        def get_new_card():
            card = session['cards'][(int(random.randint(0, len(session['cards'])-1)))]
            return card

        if len(session['cards']) == 0:
            return "you have won"

        current_card = get_new_card()
        return render_template('current_card_page.html', APP_NAME=APP_NAME, VERSION=VERSION,
                               location=current_card['location'],
                               image=current_card['image'],
                               question=current_card['question'],
                               answers=current_card['answers'],
                               correctAnswer=current_card['correctAnswer'])

    return redirect(url_for('login')), 401

@app.route('/is-answer-correct', methods=["POST"])
def is_answer_correct():
    if 'loggedin' in session:
        location = request.form['location']
        answer = request.form['answer']

        card = next(item for item in cards_dict if item["location"] == location)

        if card["correctAnswer"] == answer:
            session['cards'].remove(card)
            session.modified = True
            return "correct"
        else:
            return "incorrect"

    return redirect(url_for('login')), 401

@app.route('/scores', methods=['GET', 'POST'])
def scores():
    return render_template('scores.html', APP_NAME=APP_NAME, VERSION=VERSION)

@app.route('/gdpr-policy', methods=['GET', 'POST'])
def gdpr_policy():
    return render_template('gdpr_policy.html', APP_NAME=APP_NAME, VERSION=VERSION)

@app.route('/landing-page', methods=['GET', 'POST'])
def landing_page():
    return render_template('landing_page.html', APP_NAME=APP_NAME, VERSION=VERSION)

@app.route('/reset')
def reset():
    session['cards'] = cards_dict

    # Redirect to login page
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('landing_page'))


# ADMIN SECTION
# !SECURE # TREAT WITH CAUTION

@app.route('/adminIndex', methods=['GET'])
def adminIndex():
    if (True): # admin sesh check eventually
        return render_template("adminIndex.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return render_template("adminIndex.html", APP_NAME=APP_NAME, VERSION=VERSION)

@app.route('/adminMap', methods=['GET'])
def adminMap():
    if (True): # admin sesh check eventually
        return render_template("mapView.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return render_template("mapView.html", APP_NAME=APP_NAME, VERSION=VERSION)

@app.route('/adminUsers', methods=['GET'])
def adminUsers():
    if (True): # admin sesh check eventually
        return render_template("userList.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return render_template("userList.html", APP_NAME=APP_NAME, VERSION=VERSION)