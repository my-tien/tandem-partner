from typing import Optional

from PySide6.QtWidgets import QAbstractItemView, QListView, QVBoxLayout, QWidget
from PySide6.QtCore import Signal
from chat_history.history_model import HistoryModel
from chat_history.history_item_delegate import HistoryItemDelegate


class ChatHistoryWidget(QWidget):
    play_clicked = Signal(int)

    def __init__(self, model: HistoryModel, parent: Optional[QWidget] = None):
        super(ChatHistoryWidget, self).__init__(parent)
        self.listview = QListView(self)
        self.history_model = model
        self.item_delegate = HistoryItemDelegate(self.listview)
    
        self.listview.setModel(self.history_model)
        self.listview.setItemDelegate(self.item_delegate)

        self.listview.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.listview)
        self.setLayout(self.vlayout)

        self.history_model.rowsInserted.connect(self.listview.scrollToBottom)
        self.history_model.rowsRemoved.connect(self.listview.scrollToBottom)
