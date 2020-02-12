from flask import Flask, render_template
from flask_bootstrap import Bootstrap

APP_NAME = "ExePlore"
VERSION = "0.1"

app = Flask(__name__)
Bootstrap(app)


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", APP_NAME=APP_NAME, VERSION=VERSION)
