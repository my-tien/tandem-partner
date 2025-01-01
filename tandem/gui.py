import argparse
import os
import platform
import signal
import sys
from typing import Optional

from PySide6 import QtCore, QtGui, QtMultimedia, QtWidgets
from PySide6.QtGui import QFont

from tandem.chat_history.chat_history_widget import ChatHistoryWidget
from tandem.chat_history.history_model import HistoryModel
from tandem.char_retrieval_chain import get_character_list
from tandem.tandem_partner import TandemPartner


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

        self.tandem_partner: TandemPartner = tandem

        self.topic_label = QtWidgets.QLabel(self.tandem_partner.character_list)

        self.history_model = HistoryModel(tandem)
        self.chat_history_widget = ChatHistoryWidget(self.history_model, self)

        self.media_player = QtMultimedia.QMediaPlayer()
        self.audio_output = QtMultimedia.QAudioOutput()
        self.audio_output.setVolume(50)
        self.media_player.setAudioOutput(self.audio_output)

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

    @QtCore.Slot(int)
    def _play_text2speech(self, message_idx: int):
        self.tandem_partner.text2speech(message_idx, f"_audio/{message_idx}.mp3")
        self.media_player.setSource(QtCore.QUrl.fromLocalFile(f"_audio/{message_idx}.mp3"))
        self.media_player.play()

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

    parser = argparse.ArgumentParser()
    parser.add_argument("--dummy", action="store_true")
    parser.add_argument("--choose-topic", action="store_true")
    args = parser.parse_args()
    DUMMY_RUN = args.dummy

    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('Tandem Partner')
    app.setFont(QFont(QFont().defaultFamily(), 18))

    if DUMMY_RUN:
        character_list = """停(tíng) - stop, suspend, delay; suitable
救(jiù) - save, rescue, relieve; help, aid
外(wài) - out, outside, external; foreign
進(jìn) - advance, make progress, enter
客(kè) - guest, traveller; customer
集(jí) - assemble, collect together
越(yuè) - exceed, go beyond; the more ...
落(luò) - fall, drop; net income, surplus
待(dài) - treat, entertain, receive; wait
旅(lǚ) - travel, journey, trip"""
    else:
        if args.choose_topic:
            topic = open_topic_dialog()
            if not topic:
                QtCore.QCoreApplication.exit()

            character_list = get_character_list(topic=topic)
        else:
            character_list = get_character_list(topic="traveling")

    tandem = TandemPartner("Lang", character_list)

    window = ChatWindow(tandem)
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())