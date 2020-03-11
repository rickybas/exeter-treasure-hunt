import json
import os
from datetime import datetime

from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from flask_talisman import Talisman

from db import db

APP_NAME = "ExePlore"
VERSION = "0.4-beta"

app = Flask(__name__)

app.secret_key = 'your secret key'
app.debug = True

Talisman(app, content_security_policy=None) # Create a Talisman for the app. High security :D

# Mail stuff
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME="info@exeter.me",
    SECURITY_EMAIL_SENDER="info@exeter.me",
    MAIL_PASSWORD="1xtb7lfmuzss1y6kvuhz749r"
)

mail = Mail(app)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
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

try:
    with open('app/db/cards.json', 'r') as f:
        cards_dict = json.load(f)
except:
    with open('db/cards.json', 'r') as f:
        cards_dict = json.load(f)

db = db(mysql, bcrypt, cards_dict)

try:
    if not os.path.exists('app/db/progress.csv'):
        with open('app/db/progress.csv', 'w'): pass
except:
    if not os.path.exists('db/progress.csv'):
        with open('db/progress.csv', 'w'): pass

# HTTPS redirect --------------------------------------------------------------

@app.before_request
def before_request():
    if not request.is_secure and app.env != "development" and app.debug != True:
        url = request.url.replace("http://", "https://", 1)
        code = 301
        return redirect(url, code=code)


# Tasks ----------------------------------------------------------------------------------------------------------------

@scheduler.task('interval', id='do_save_progress', seconds=3600, misfire_grace_time=5)
def do_save_progress_job():
    with app.app_context():
        progress = db.get_overall_progress()
        with open("app/db/progress.csv", 'a') as f:
            f.write(str(progress) + ',' + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '\n')


# Static pages ---------------------------------------------------------------------------------------------------------

@app.route('/landing-page', methods=['GET'])
def landing_page():
    return render_template('landing_page.html', APP_NAME=APP_NAME, VERSION=VERSION)


@app.route('/gdpr-policy', methods=['GET'])
def gdpr_policy():
    return render_template('gdpr_policy.html', APP_NAME=APP_NAME, VERSION=VERSION)

@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html', APP_NAME=APP_NAME, VERSION=VERSION)


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

        msg = db.successful_login(request.form['username'], request.form['password'], request.form['consent'])
        if msg is None:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', APP_NAME=APP_NAME, VERSION=VERSION, msg=msg), 401

    return render_template('login.html', APP_NAME=APP_NAME, VERSION=VERSION)


@app.route('/card/<location>', methods=["GET"])
def single_card(location):
    if 'loggedin' in session:
        try:
            card = next(item for item in cards_dict if item["location"] == location)
        except:
            return "location not found", 404

        if location not in db.get_owned_cards_by_user(session['username']):
            return "don't own card"

        return render_template('current_card_page.html', APP_NAME=APP_NAME, VERSION=VERSION,
                               username=session['username'],
                               location=card['location'],
                               image=card['image'],
                               question=card['question'],
                               answers=card['answers'],
                               correctAnswer=card['correctAnswer'],
                               won_cards=db.get_completed_cards_by_user(session['username']))

    return redirect(url_for('login'), code=401)

@app.route('/my-help-requests', methods=['GET'])
def my_help_requests():
    if 'loggedin' in session:
        return render_template("my_help_requests.html", APP_NAME=APP_NAME, VERSION=VERSION,
                               help_requests=db.get_help_requests_by_user(session['username']))

    return redirect(url_for('login'))


@app.route('/add-help-request', methods=['GET', 'POST'])
def add_help_request():
    if 'loggedin' in session:
        if request.method == 'POST':
            if 'description' in request.form and \
                    db.add_help_request(session['username'], request.form['description']):
                return redirect(url_for('my_help_requests'))
            else:
                return render_template('add_help_request.html', APP_NAME=APP_NAME, VERSION=VERSION, msg="Failed to send")

        return render_template('add_help_request.html', APP_NAME=APP_NAME, VERSION=VERSION)

    return redirect(url_for('login'))

@app.route('/reset')
def reset():
    db.reset_my_cards(session['username'])

    # Redirect to login page
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('landing_page'))

@app.route('/scan-card', methods=['GET', 'POST'])
def scan_card():
    return render_template('scan_card.html', APP_NAME=APP_NAME, VERSION=VERSION)


# AJAX -------------------------------------------------------------------------

@app.route('/scores')
def scores():
    if 'loggedin' in session:
        return render_template('scores.html', APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'])

    return redirect(url_for('login'))


@app.route('/map')
def map():
    if 'loggedin' in session:
        return render_template('map.html', APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'])

    return redirect(url_for('login'))


@app.route('/cards')
def cards():
    if 'loggedin' in session:
        return render_template('cards.html', APP_NAME=APP_NAME, VERSION=VERSION, username=session['username'],
                               cards=cards_dict,
                               owned_cards=db.get_owned_cards_by_user(session['username']),
                               won_cards=db.get_completed_cards_by_user(session['username']))

    return redirect(url_for('login'))

@app.route('/loadcards', methods=['GET'])
def load_cards():
    if 'loggedin' in session:
        return jsonify(cards_dict)    
    return redirect(url_for('login'))


@app.route('/add-card-to-deck/<location>', methods=["GET"])
def add_card_to_deck(location):
    if 'loggedin' in session:
        try:
            next(item for item in cards_dict if item["location"] == location)
        except:
            return "location not found", 400

        if not db.add_card_to_deck(session['username'], location):
            return "error"

        return "added"

    return redirect(url_for('login'))

@app.route('/is-answer-correct', methods=["POST"])
def is_answer_correct():
    if 'loggedin' in session:
        location = request.form['location']
        answer = request.form['answer']

        try:
            card = next(item for item in cards_dict if item["location"] == location)
        except:
            return "location not found", 400

        if card["correctAnswer"] == answer:
            if location in db.get_completed_cards_by_user(session['username']):
                return "Correct but already won card"

            if not db.add_won_card(session['username'], location):
                return "Error"

            if len(db.get_completed_cards_by_user(session['username'])) == len(cards_dict):
                return "YOU HAVE WON"

            if len(db.get_owned_cards_by_user(session['username'])) == len(cards_dict):
                return "Correct. No more new cards to give, keep answering more"

            if db.give_user_new_random_card(session['username']):
                return "Correct, new card given"

            return "Error"
        else:
            return "Incorrect"

    return redirect(url_for('login'))

@app.route('/open-help-request/<id>', methods=["GET"])
def open_help_request(id):
    if 'loggedin' in session:
        if db.open_help_request(session['username'], id):
            if session['username'] == "admin":
                return redirect(url_for('admin_help_requests'))
            else:
                return redirect(url_for('my_help_requests'))
        else:
            return "does not exist"

    return redirect(url_for('login'))

@app.route('/close-help-request/<id>', methods=["GET"])
def close_help_request(id):
    if 'loggedin' in session:
        if db.close_help_request(session['username'], id):
            if session['username'] == "admin":
                return redirect(url_for('admin_help_requests'))
            else:
                return redirect(url_for('my_help_requests'))
        else:
            return "does not exist", 404

    return redirect(url_for('login'))


# Admin section --------------------------------------------------------------------------------------------------------

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST' and \
            'username' in request.form and \
            'password' in request.form and \
            request.form['username'] == "admin":

        msg = db.successful_login(request.form['username'], request.form['password'])

        if msg is None:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['username'] = "admin"
            return redirect(url_for('admin_index'))
        else:
            return render_template('admin_login.html', APP_NAME=APP_NAME, VERSION=VERSION,
                                   msg=msg), 401

    return render_template('admin_login.html', APP_NAME=APP_NAME, VERSION=VERSION)


@app.route('/admin-index', methods=['GET'])
def admin_index():
    if 'loggedin' in session and session['username'] == "admin":
        won_cards = db.get_all_owned_cards()
        users = db.get_all_users()

        return render_template("admin_index.html", APP_NAME=APP_NAME, VERSION=VERSION,
                               cards_dict=cards_dict,
                               num_won_cards=len(won_cards),
                               num_users=len(users),
                               num_active_users=db.get_num_of_active_players(),
                               num_of_open_help_requests = db.get_num_of_open_help_requests(),
                               overall_progress=round(db.get_overall_progress(), 2),
                               overall_progress_over_time=db.get_overall_progress_over_time(),
                               won_card_distribution=db.owned_card_distribution(),
                               top_locations_by_playerbase_ownership=db.top_locations_by_playerbase_ownership())

    return redirect(url_for('admin_login'))


@app.route('/admin-map', methods=['GET'])
def admin_map():
    if 'loggedin' in session and session['username'] == "admin":
        return render_template("map_view.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return redirect(url_for('admin_login'))


@app.route('/admin-users', methods=['GET'])
def admin_users():
    if 'loggedin' in session and session['username'] == "admin":
        return render_template("user_list.html", APP_NAME=APP_NAME, VERSION=VERSION)

    return redirect(url_for('admin_login'))


@app.route('/admin-help-requests', methods=['GET'])
def admin_help_requests():
    if 'loggedin' in session and session['username'] == "admin":
        return render_template("admin_help_requests.html", APP_NAME=APP_NAME, VERSION=VERSION,
                               help_requests=db.get_all_help_requests())

    return redirect(url_for('admin_login'))

@app.route('/generate-report', methods=['GET'])
def generate_report():
    if 'loggedin' in session and session['username'] == "admin":
        return "report"

    return redirect(url_for('admin_login'))


# Mail  ----------------------------------------------------------------------------------------------------------------

@app.route('/testMail', methods=['GET'])
def testMail():
    msg = mail.send_message(
        subject='Anthony Test Mail Thingy',
        sender="info@exeter.me",
        recipients=["arb239@exeter.ac.uk"],
        html="Congratulations Anthony! You have sent an email from our Flask server."
    )
    return "<h1>Sent mail</h1>"
