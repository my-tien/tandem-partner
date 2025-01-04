from datetime import datetime
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, Slot
from tandem.tandem_partner import TandemPartner


class HistoryItem:
    def __init__(self, message: str, author: str, timestamp: int):
        self.author = author
        self.timestamp = timestamp

        self.traditional = ""
        self.pinyin = ""
        self.english = ""
        parts = message.split('---')
        if len(parts) > 0:
            self.traditional = parts[0].strip()
        if len(parts) > 1:
            self.pinyin = parts[1].strip()
        if len(parts) > 2:
            self.english = parts[2].strip()

    def timestamp_str(self):
        return datetime.fromtimestamp(self.timestamp).strftime("%Y-%m-%dT%H:%M:%S")


class HistoryModel(QAbstractListModel):
    _HEADER = ("Message", "Author", "Timestamp")

    def __init__(self, tandem: TandemPartner):
        super(HistoryModel, self).__init__()
        self.tandem = tandem
        self.response_worker = None

    def add_message(self, author: str, message: str):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.insertRow(self.rowCount(), QModelIndex())
        self.response_worker = self.tandem.invoke(author, message)
        self.endInsertRows()
        self.response_worker.response_received.connect(self.handle_response, Qt.ConnectionType.SingleShotConnection)
        self.response_worker.start()

    def add_dummy_message(self, author: str, message: str):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount() + 1)
        self.insertRows(self.rowCount(), 2, QModelIndex())
        self.tandem.dummy_invoke(author, message)
        self.tandem.handle_response("""你好！要不要聊聊關於停車的話題？
---
Nǐ hǎo! Yào bù yào liáo liáo guān yú tíngchē de huàtí?
---
Hello! Do you want to talk about the topic of parking? ihfasdlöfalksdf asjdfeeef
Hello! Do you want to talk about the topic of parking? ihfasdlöfalksdf Hello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdfHello! Do you want to talk about the topic of parking? ihfasdlöfalksdf""")
        self.endInsertRows()

    @Slot(str)
    def handle_response(self, response: str):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.tandem.handle_response(response)
        self.endInsertRows()

    def rowCount(self, parent = QModelIndex()) -> int:
        return len(self.tandem.chat_history.messages)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int) -> tuple[str]:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return HistoryModel._HEADER
        return None

    def data(self, index: QModelIndex, role: int) -> HistoryItem:
        if role == Qt.ItemDataRole.DisplayRole:
            msg = self.tandem.chat_history.messages[index.row()]
            item = HistoryItem(
                message=msg.content,
                author=msg.additional_kwargs["author"],
                timestamp=msg.additional_kwargs["timestamp"]
            )
            return item
