from flask import Flask, render_template
from flask import request
from datetime import datetime
import random

app = Flask(__name__)

def _get_time():
    return datetime.now().strftime("%H:%M:%S")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat")
def chat():
    topic = request.args.get("topic")
    if not topic:
        return ('', 204)

    return render_template("chat.html", topic=topic)


@app.route("/chat/message", methods=['GET', 'POST'])
def chat_message():
    message = request.form.get("message")
    topic = request.args.get("topic")
    if not topic or not message:
        return ('', 204)

    return render_template("message.html",
        name="Student", message=message, time=_get_time(), topic=topic)


@app.route("/chat/response")
def chat_response():
    topic = request.args.get("topic")
    if not topic or not random.choice([True, False]):
        return ('', 204)
    return render_template("response.html", name="Lang", message="我愛寵物", time=_get_time())
