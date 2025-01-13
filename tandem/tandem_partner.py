from datetime import datetime
from dotenv import load_dotenv
if not load_dotenv(override=True):
    raise ValueError("Failed to load OPENAI_API_KEY")

from pathlib import Path

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from openai import OpenAI
from PySide6.QtCore import QObject, QThread, Signal, Slot
from tandem.conversation_chain import get_tandem_chain, get_simplified_traditional_converter_chain


class ResponseWorker(QThread):
    response_received = Signal(str)

    def __init__(self, chain, message):
        super(ResponseWorker, self).__init__()
        self.chain = chain
        self.message = message

    def run(self):
        response = self.chain.invoke({"input": self.message})
        self.response_received.emit(response)


class Response:
    def __init__(self, msg, idx):
        self.idx = idx
        self.traditional = ""
        self.pinyin = ""
        self.english = ""
        parts = msg.split('---')
        if len(parts) > 0:
            self.traditional = parts[0].strip()
        if len(parts) > 1:
            self.pinyin = parts[1].strip()
        if len(parts) > 2:
            self.english = parts[2].strip()


class TandemPartner(QObject):
    response_signal = Signal(Response)

    def __init__(self, name: str, stories: str):
        super(TandemPartner, self).__init__()
        tandem_chain = get_tandem_chain(stories)
        converter_chain = get_simplified_traditional_converter_chain()

        self.name = name
        self.stories = stories
        self.chain = {"input": tandem_chain} | converter_chain
        self.worker = None
        self.chat_history = ChatMessageHistory()
        self.history_length = 0
        self.openai_client = OpenAI()
    
    def reset_history(self):
        self.chat_history = ChatMessageHistory()
        self.history_length = 0

    def _add_user_message(self, message: HumanMessage):
        self.chat_history.add_user_message(message)
        self.history_length += 1

    def _add_ai_message(self, message: AIMessage) -> int:
        self.chat_history.add_ai_message(message)
        message_idx = self.history_length
        self.history_length += 1
        return message_idx

    def invoke(self, author: str, message: str) -> ResponseWorker:
        message = HumanMessage(content=message, additional_kwargs={
            "author": author,
            "timestamp": datetime.now().timestamp()
        })
        self._add_user_message(message)
        return ResponseWorker(self.chain, self.chat_history)

    @Slot(str)
    def dummy_invoke(self, author: str, message: str):
        message = HumanMessage(content=message, additional_kwargs={
            "author": author,
            "timestamp": datetime.now().timestamp()
        })
        self._add_user_message(message)

    @Slot(str)
    def handle_response(self, response: str):
        response = AIMessage(content=response, additional_kwargs={
            "author": self.name,
            "timestamp": datetime.now().timestamp()
        })
        self._add_ai_message(response)

    def text2speech(self, history_index: int, output_path: str):
        Path(output_path).parent.mkdir(exist_ok=True, parents=True)
        if not Path(output_path).exists():
            message = self.chat_history.messages[history_index]
            chinese = Response(message.content, history_index).traditional
            response = self.openai_client.audio.speech.create(model="tts-1", voice="nova", input=chinese, response_format="mp3")
            response.stream_to_file(output_path)
