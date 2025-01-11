from typing import Optional

from PySide6.QtWidgets import QAbstractItemView, QListView, QVBoxLayout, QWidget
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Signal
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

        self.history_model.rowsInserted.connect(self.animateScrollToBottom)
        self.history_model.rowsRemoved.connect(self.animateScrollToBottom)

    def animateScrollToBottom(self):
        if self.history_model.rowCount() > 0:
            bar = self.listview.verticalScrollBar()
            current_value = bar.value()

            # force calculation of maximum
            self.listview.scrollToBottom()

            bar.setValue(current_value)
            self.animateScrollTo(bar.maximum())

    def animateScrollTo(self, y: int):
        scroll_animation = QPropertyAnimation(
            self.listview.verticalScrollBar(), b"value", self
        )

        scroll_animation.setStartValue(self.listview.verticalScrollBar().value())

        scroll_animation.setEndValue(y)
        scroll_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        scroll_animation.setDuration(500)
        scroll_animation.start()
