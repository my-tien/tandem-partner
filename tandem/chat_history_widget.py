from contextlib import contextmanager
from datetime import datetime
import re
from typing import Optional

from PySide6 import QtCore, QtWidgets
from PySide6 import QtGui
from PySide6.QtCore import Signal
from tandem_partner import Response


def _get_time_label_short(d: datetime):
    return d.strftime("%H:%M:%S")


def _get_time_label_long(d: datetime):
    return d.strftime("%Y-%m-%dT%H:%M:%S")

class ChatHistoryWidget(QtWidgets.QTextEdit):
    play_clicked = Signal(int)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        super(ChatHistoryWidget, self).__init__(parent)
        self.setReadOnly(True)
        self.hovered_anchor = None

    @contextmanager
    def chinese_font_context(self):
        current_font = self.currentFont()
        self.setCurrentFont("TW-MOE-Std-Kai")
        self.setFontPointSize(18)
        try:
            yield
        finally:
            self.setCurrentFont(current_font)

    def _display_user_message(self, name: str, message: str):
        response_time = datetime.now()
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.insertPlainText(f"\n[{name}] {_get_time_label_short(response_time)}:\n")
        with self.chinese_font_context():
            self.insertPlainText(message)
        self.insertPlainText("\n")
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def _display_lang_response(self, name: str, message: Response):
        response_time = datetime.now()

        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.insertPlainText("\n")

        cursor = self.textCursor()
        plainFormat = cursor.charFormat()
        anchorFormat = QtGui.QTextCharFormat()
        anchorFormat.setAnchor(True)
        anchorFormat.setAnchorHref(f"{message.idx}")
        anchorFormat.setToolTip("Play Lang response")
        cursor.insertText("[⏵︎]", anchorFormat)

        cursor.insertText(f" [{name}] {_get_time_label_short(response_time)}:\n", plainFormat)
        with self.chinese_font_context():
            self.insertPlainText(f"{message.traditional}")
        self.insertPlainText(f"\n\n{message.pinyin}\n\n{message.english}\n")
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        self.hovered_anchor = self.anchorAt(event.pos())
        if self.hovered_anchor:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        else:
            QtWidgets.QApplication.restoreOverrideCursor()

    def mouseReleaseEvent(self, _):
        # only do something if we hovered over an anchor before pressing.
        if isinstance(self.hovered_anchor, str):
            self.play_clicked.emit(int(self.hovered_anchor))
        else:
            QtWidgets.QApplication.restoreOverrideCursor()
