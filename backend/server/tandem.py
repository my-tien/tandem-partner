from flask import Flask, render_template
from flask import request, redirect
from flask_htmx import HTMX
from datetime import datetime

app = Flask(__name__)
htmx = HTMX(app)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    message = request.form.get("message")
    if message:
        return render_template("message.html", name="Student", message=message, time=datetime.now().strftime("%H:%M:%S"))
    topic = request.args.get("topic")
    if topic:
        return render_template("chat.html", topic=topic)
    return redirect("/")
    
