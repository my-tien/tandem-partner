import argparse
import os
import platform
import signal
import sys

from typing import Optional

from PySide6.QtCore import Qt, QUrl, Slot
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
    def __init__(self, tandem: TandemPartner, stories: dict[str, str]):
        super(ChatWindow, self).__init__()

        self.setWindowTitle("Conversation with Lang")
        width = 1280
        height = 720
        self.setGeometry(0, 0, width, height)

        self.tandem_partner = tandem
        self.stories = stories
        self.current_story = None

        self.choose_story_button = QPushButton("Choose story…", self)
        self.choose_story_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.story_label = QLabel("")
        self.story_label.setFont(QFont("TW-MOE-Std-Kai", pointSize=18))
        self.story_label.setWordWrap(True)
        self.start_chat_button = QPushButton("Start chatting with Lang")
        self.start_chat_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.start_chat_button.setDisabled(True)

        self.history_model = HistoryModel(tandem)
        self.chat_history_widget = ChatHistoryWidget(self.history_model, self)
        self.chat_history_widget.setDisabled(True)

        self.media_player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.audio_output.setVolume(50)
        self.media_player.setAudioOutput(self.audio_output)

        self.message_input = QLineEdit()
        self.message_input.setFont(QFont("TW-MOE-Std-Kai", pointSize=18))
        self.message_input.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.message_input.setPlaceholderText("Type a message…")
        self.message_input.setDisabled(True)
        self.send_button = QPushButton("Send")
        self.send_button.setDisabled(True)

        self.vlayout = QVBoxLayout()
        self.vlayout.addWidget(self.choose_story_button, alignment=Qt.AlignmentFlag.AlignLeft)
        self.vlayout.addWidget(self.story_label)
        self.vlayout.addWidget(self.start_chat_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.vlayout.addWidget(Separator())
        self.vlayout.addWidget(self.chat_history_widget)
        self.vlayout.addWidget(Separator())
        self.vlayout.addWidget(self.message_input)
        self.vlayout.addWidget(self.send_button)

        central_widget = QWidget()
        central_widget.setLayout(self.vlayout)
        self.setCentralWidget(central_widget)

        self.choose_story_button.clicked.connect(self._choose_story_dialog)
        self.start_chat_button.clicked.connect(self._start_chat_clicked)
        self.message_input.textChanged.connect(self._message_input_changed)
        self.message_input.returnPressed.connect(self._send_button_clicked)
        self.send_button.clicked.connect(self._send_button_clicked)
        self.chat_history_widget.play_clicked.connect(self._play_text2speech)

    def showEvent(self, event):
        super(ChatWindow, self).showEvent(event)
        self.message_input.setFocus()

    def set_story(self, story: Optional[str]):
        self.current_story = story
        if story and story in self.stories:
            self.story_label.setText(f"{story}\n\n{self.stories[story]}")
            self.start_chat_button.setEnabled(True)
        else:
            self.story_label.setText("")
            self.start_chat_button.setEnabled(False)

    def enable_chat(self):
        self.chat_history_widget.setEnabled(True)
        self.message_input.setEnabled(True)
        self.send_button.setEnabled(True)

    def enable_send(self):
        self.send_button.setEnabled(len(self.message_input.text()) > 0)

    def _choose_story_dialog(self):
        story, ok = QInputDialog.getItem(
            self, "Choose a story to talk about", "Story:", self.stories.keys()
        )
        if ok and story:
            self.set_story(story)

    def _start_chat_clicked(self):
        self.history_model.response_handled.connect(self.enable_chat, Qt.ConnectionType.SingleShotConnection)
        self.history_model.start_new_chat(self.current_story) 

    def _message_input_changed(self, text):
        self.send_button.setEnabled = len(text) > 0

    def _send_button_clicked(self):
        message = self.message_input.text()
        self.message_input.setText("")
        if DUMMY_RUN:
            self.history_model.add_dummy_message("Student", message)
        else:
            self.send_button.setDisabled(True)
            self.history_model.response_handled.connect(self.enable_send, Qt.ConnectionType.SingleShotConnection)
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


def parse_stories(stories_doc: str) -> dict[str, str]:
    stories_dict = {}
    title = None
    start = 0
    while start < len(stories_doc):
        title_end = stories_doc.find("\n\n", start)
        if title_end == -1:
            raise ValueError("Malformed document: ")
        story_end = stories_doc.find("\n\n\n", title_end)
        if story_end == -1:
            story_end = len(stories_doc)
        title = stories_doc[start:title_end]
        story = stories_doc[title_end + len("\n\n"):story_end]
        stories_dict[title] = story
        start = min(story_end + len("\n\n\n"), len(stories_doc))
    return stories_dict

if __name__ == '__main__':
    if platform.system() == "linux":
        os.environ["QT_IM_MODULE"] = "fcitx"

    parser = argparse.ArgumentParser()
    parser.add_argument("--dummy", action="store_true")
    args = parser.parse_args()
    DUMMY_RUN = args.dummy

    app = QApplication(sys.argv)
    app.setApplicationName('Tandem Partner')
    app.setFont(QFont(QFont().defaultFamily(), 18))

    with open("data/新編初級說話課本.txt", "r", encoding="utf8") as f:
        stories_doc = f.read()
    stories_dict = parse_stories(stories_doc)

    tandem = TandemPartner("Lang", stories_doc)
    window = ChatWindow(tandem, stories_dict)
    window.show()

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    sys.exit(app.exec())