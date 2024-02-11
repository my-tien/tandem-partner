from dotenv import load_dotenv
load_dotenv(override=True)

from datetime import datetime

from flask import render_template
from flask import request
import html
from langchain_core.messages import AIMessage, HumanMessage
from tandem.char_retrieval_chain import get_character_list
from tandem.conversation_chain import get_contextualizer_chain, get_tandem_partner
from flask import Flask

app = Flask(__name__)


class Tandem:
    _partner = {}
    
    def __init__(self, topic: str):
        character_list = html.escape(get_character_list(topic=topic))
        character_list = "\n".join((f"<li>{item}</li>" for item in character_list.split("\n")))
        self.character_list = f"<ul>{character_list}</ul>"
        self.tandem_partner = get_tandem_partner(self.character_list)
        self.contextualizer = get_contextualizer_chain()
        self.chat_history = []
        self.user_message = None
        self.partner_response = None

    def __new__(cls, topic, *args, **kwargs):
        if Tandem._partner.get(topic) is None:
            new_tandem = super(Tandem, cls).__new__(cls, *args, **kwargs)
            Tandem._partner[topic] = new_tandem
        return Tandem._partner[topic]
    
    def set_user_message(self, message: str):
        if len(self.chat_history) > 0:
            message = self.contextualizer.invoke({"input": message, "chat_history": self.chat_history})
        self.user_message = message

    async def gen_answer(self):
        response = await self.tandem_partner.ainvoke({'input': self.user_message})
        self.chat_history.extend([HumanMessage(content=self.user_message), AIMessage(content=response)])
        self.partner_response = response

    def poll_response(self):
        if self.partner_response is not None:
            response = self.partner_response
            self.partner_response = None
            return response
        return None


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
    tandem = Tandem(topic)
    return render_template("chat.html", topic=topic, character_list=tandem.character_list)


@app.route("/chat/message", methods=['GET', 'POST'])
def chat_message():
    message = request.form.get("message")
    topic = request.args.get("topic")
    if not topic or not message:
        return ('', 204)

    tandem = Tandem(topic)
    tandem.set_user_message(message)
    tandem.gen_answer()
    return render_template("message.html",
        name="Student", message=message, contextualized_message=tandem.user_message, time=_get_time(), topic=topic)


@app.route("/chat/response")
def chat_response():
    topic = request.args.get("topic")
    if topic:
        response = Tandem(topic).poll_response()
        if response:
            return render_template("response.html", name="Lang", message=response, time=_get_time())
    return ('', 204)
