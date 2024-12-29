from typing import Optional

from PySide6.QtWidgets import QAbstractItemView, QTreeView, QVBoxLayout, QWidget
from PySide6.QtCore import Signal
from chat_history.history_model import HistoryModel
from chat_history.history_item_delegate import HistoryItemDelegate


class ChatHistoryWidget(QWidget):
    play_clicked = Signal(int)

    def __init__(self, model: HistoryModel, parent: Optional[QWidget] = None):
        super(ChatHistoryWidget, self).__init__(parent)
        self.history_model = model
        self.treeview = QTreeView(self)
        self.treeview.setModel(self.history_model)
        self.treeview.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.item_delegate = HistoryItemDelegate()
        self.treeview.setItemDelegate(self.item_delegate)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.treeview)
        self.setLayout(self.vlayout)
