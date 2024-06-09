from langchain.memory import ChatMessageHistory
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
    def __init__(self, msg):
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

    def __init__(self, character_list):
        super(TandemPartner, self).__init__()
        tandem_chain = get_tandem_chain(character_list)
        converter_chain = get_simplified_traditional_converter_chain()

        self.character_list = character_list
        self.chain = {"input": tandem_chain} | converter_chain
        self.worker = None
        self.chat_history = ChatMessageHistory()
    
    def invoke(self, message: str):
        self.chat_history.add_user_message(message)
        self.worker = ResponseWorker(self.chain, self.chat_history)
        self.worker.response_received.connect(self.handle_response)
        self.worker.start()

    @Slot(str)
    def handle_response(self, response):
        self.worker.response_received.disconnect(self.handle_response)
        self.chat_history.add_ai_message(response)
        self.response_signal.emit(response)
