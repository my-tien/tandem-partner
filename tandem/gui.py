import argparse
import os
import platform
import signal
import sys

from typing import Optional

from PySide6.QtCore import QCoreApplication, Qt, QUrl, Slot
from PySide6.QtGui import QFont
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget
)

from tandem.chat_history.chat_history_widget import ChatHistoryWidget
from tandem.chat_history.history_model import HistoryModel
from tandem.tandem_partner import TandemPartner


class Separator(QFrame):
    def __init__(self, parent: Optional[QWidget] = None):
        super(Separator, self).__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)


class ChatWindow(QMainWindow):
    def __init__(self, tandem):
        super(ChatWindow, self).__init__()

        self.setWindowTitle("Conversation with Lang")
        width = 1280
        height = 720
        self.setGeometry(0, 0, width, height)

        self.tandem_partner: TandemPartner = tandem

        self.topic_label = QLabel("")#self.tandem_partner.character_list)

        self.history_model = HistoryModel(tandem)
        self.chat_history_widget = ChatHistoryWidget(self.history_model, self)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(50)
        self.media_player.setAudioOutput(self.audio_output)

        self.message_input = QLineEdit()
        self.message_input.setFont(QFont("TW-MOE-Std-Kai", pointSize=18))
        self.message_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.message_input.setPlaceholderText("Type a message…")
        self.send_button = QPushButton("Send")

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.topic_label)
        self.vlayout.addWidget(Separator())
        self.vlayout.addWidget(self.chat_history_widget)
        self.vlayout.addWidget(Separator())
        self.vlayout.addWidget(self.message_input)
        self.vlayout.addWidget(self.send_button)

        central_widget = QWidget()
        central_widget.setLayout(self.vlayout)
        self.setCentralWidget(central_widget)

        self.message_input.textChanged.connect(self._message_input_changed)
        self.message_input.returnPressed.connect(self._send_button_clicked)
        self.send_button.clicked.connect(self._send_button_clicked)
        self.chat_history_widget.play_clicked.connect(self._play_text2speech)

    def showEvent(self, event):
        super(ChatWindow, self).showEvent(event)
        self.message_input.setFocus()

    def _message_input_changed(self, text):
        self.send_button.setEnabled = len(text) > 0

    def _send_button_clicked(self):
        message = self.message_input.text()
        self.message_input.setText("")
        if DUMMY_RUN:
            self.history_model.add_dummy_message("Student", message)
        else:
            self.history_model.add_message("Student", message)

    @Slot(int)
    def _play_text2speech(self, message_idx: int):
        self.tandem_partner.text2speech(message_idx, f"_audio/{message_idx}.mp3")
        self.media_player.setSource(QUrl.fromLocalFile(f"_audio/{message_idx}.mp3"))
        self.media_player.play()

def open_topic_dialog():
    topic, ok = QInputDialog.getText(
        None,
        "Choose a topic for conversation",
        "topic"
    )
    return topic if ok else None


if __name__ == '__main__':
    if platform.system() == "linux":
        os.environ["QT_IM_MODULE"] = "fcitx"

    parser = argparse.ArgumentParser()
    parser.add_argument("--dummy", action="store_true")
    parser.add_argument("--choose-topic", action="store_true")
    args = parser.parse_args()
    DUMMY_RUN = args.dummy

    app = QApplication(sys.argv)
    app.setApplicationName('Tandem Partner')
    app.setFont(QFont(QFont().defaultFamily(), 18))

    if DUMMY_RUN:
        stories = ""
    else:
        if args.choose_topic:
            topic = open_topic_dialog()
            if not topic:
                QCoreApplication.exit()
        else:
            with open(r"data\新編初級說話課本.txt", "r", encoding="utf8") as f:
                stories = f.read()

    tandem = TandemPartner("Lang", stories)

    window = ChatWindow(tandem)
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())