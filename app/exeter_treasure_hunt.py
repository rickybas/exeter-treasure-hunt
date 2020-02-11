from flask import Flask, render_template

APP_NAME = "ExePlore"
VERSION = "0.1"

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return render_template("index.html", APP_NAME=APP_NAME)
