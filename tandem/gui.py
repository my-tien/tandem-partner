from contextlib import contextmanager
from datetime import datetime
import os
import platform
import signal
import sys
from typing import Optional

from PySide6 import QtCore, QtWidgets
from PySide6 import QtGui

from tandem.char_retrieval_chain import get_character_list
from tandem_partner import Response, TandemPartner


def _get_time():
    return datetime.now().strftime("%H:%M:%S")


class Separator(QtWidgets.QFrame):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super(Separator, self).__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)


class ChatWindow(QtWidgets.QMainWindow):
    def __init__(self, tandem):
        super(ChatWindow, self).__init__()

        self.setWindowTitle("Conversation with Lang")
        width = 1280
        height = 720
        self.setGeometry(0, 0, width, height)
        screen = QtGui.QScreen().geometry()
        self.move((screen.width() - width) // 2, (screen.height() - height) // 2)

        self.tandem_partner = tandem

        self.topic_label = QtWidgets.QLabel(self.tandem_partner.character_list)

        self.chat_history_widget = QtWidgets.QTextEdit(self)
        self.chat_history_widget.setReadOnly(True)

        self.message_input = QtWidgets.QLineEdit()
        self.message_input.setFont(QtGui.QFont("TW-MOE-Std-Kai", pointSize=18))
        self.message_input.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.message_input.setPlaceholderText("Type a message…")
        self.send_button = QtWidgets.QPushButton("Send")

        self.vlayout = QtWidgets.QVBoxLayout()
        self.vlayout.addWidget(self.topic_label)
        self.vlayout.addWidget(Separator())
        self.vlayout.addWidget(self.chat_history_widget)
        self.vlayout.addWidget(Separator())
        self.vlayout.addWidget(self.message_input)
        self.vlayout.addWidget(self.send_button)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.vlayout)
        self.setCentralWidget(central_widget)

        self.message_input.textChanged.connect(self._message_input_changed)
        self.message_input.returnPressed.connect(self._send_button_clicked)
        self.send_button.clicked.connect(self._send_button_clicked)
        self.tandem_partner.response_signal.connect(self._display_response)

    def showEvent(self, event):
        super(ChatWindow, self).showEvent(event)
        self.message_input.setFocus()

    def _message_input_changed(self, text):
        self.send_button.setEnabled = len(text) > 0

    @contextmanager
    def chinese_font_context(self):
        current_font = self.chat_history_widget.currentFont()
        self.chat_history_widget.setCurrentFont("TW-MOE-Std-Kai")
        self.chat_history_widget.setFontPointSize(18)
        try:
            yield
        finally:
            self.chat_history_widget.setCurrentFont(current_font)

    def _display_user_message(self, name: str, message: str):
        self.chat_history_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.chat_history_widget.insertPlainText(f"\n[{name}] {_get_time()}:\n")
        with self.chinese_font_context():
            self.chat_history_widget.insertPlainText(message)
        self.chat_history_widget.insertPlainText("\n")
        self.chat_history_widget.verticalScrollBar().setValue(self.chat_history_widget.verticalScrollBar().maximum())

    def _display_lang_response(self, name: str, message: Response):
        self.chat_history_widget.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.chat_history_widget.insertPlainText(f"\n[{name}] {_get_time()}:\n")
        with self.chinese_font_context():
            self.chat_history_widget.insertPlainText(f"{message.traditional}")
        self.chat_history_widget.insertPlainText(f"\n\n{message.pinyin}\n\n{message.english}\n")
        self.chat_history_widget.verticalScrollBar().setValue(self.chat_history_widget.verticalScrollBar().maximum())

    def _send_button_clicked(self):
        message = self.message_input.text()
        self.message_input.setText("")
        self._display_user_message("Student", message)
        self.tandem_partner.invoke(message)

    @QtCore.Slot(Response)
    def _display_response(self, response: Response):
        self._display_lang_response("Lang", response)


def open_topic_dialog():
    topic, ok = QtWidgets.QInputDialog.getText(
        None,
        "Choose a topic for conversation",
        "topic"
    )
    return topic if ok else None


if __name__ == '__main__':
    if platform.system() == "linux":
        os.environ["QT_IM_MODULE"] = "fcitx"
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Tandem Partner')

    topic = open_topic_dialog()
    if not topic:
        QtCore.QCoreApplication.exit()

    character_list = get_character_list(topic="traveling")
    tandem = TandemPartner(character_list)

    window = ChatWindow(tandem)
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())