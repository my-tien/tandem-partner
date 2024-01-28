from flask import Flask, render_template
from flask import request
from flask_htmx import HTMX


app = Flask(__name__)
htmx = HTMX(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/topic", methods=['GET', 'POST'])
def topic():
    print("request body", request.form)
    return render_template("topic.html", context={"topic": request.form["topic"]})