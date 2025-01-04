from PySide6.QtCore import Qt, QModelIndex, QRect, QSize
from PySide6.QtGui import QPainter, QStaticText
from PySide6.QtWidgets import QApplication, QStyledItemDelegate, QStyleOptionViewItem, QTreeView
from chat_history.history_model import HistoryItem


_PAD = 8


class HistoryItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTreeView = None):
        super(HistoryItemDelegate, self).__init__(parent)
        self.view = parent

    def get_painted_message(self, index: QModelIndex):
        item : HistoryItem = index.data()
        message = "\n\n".join((item.traditional, item.pinyin, item.english)).rstrip("\n")
        return message

    def get_rects(self, option: QStyleOptionViewItem, index: QModelIndex):
        message = self.get_painted_message(index)
        option_rect = option.rect
        font_metrics = QApplication.fontMetrics()
        max_width = option_rect.width() - 2 * _PAD

        msg_rect_no_wrap = font_metrics.boundingRect(message)

        text_width = min(msg_rect_no_wrap.width() + _PAD, max_width)

        x = option_rect.left() + _PAD
        y = option_rect.top() + _PAD
        even_row = index.row() & 1 == 0
        if even_row:
            x = option_rect.left() + option_rect.width() - text_width - 2 * _PAD

        msg_rect = font_metrics.boundingRect(
            x, y, text_width, msg_rect_no_wrap.height(), Qt.TextFlag.TextWordWrap, message
        )

        return msg_rect

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item : HistoryItem = index.data()
        message = self.get_painted_message(index)

        self.initStyleOption(option, index)
        msg_rect = self.get_rects(option, index)
        
        even_row = index.row() & 1 == 0

        painter.save()

        msg_rect = painter.boundingRect(msg_rect, Qt.TextFlag.TextWordWrap, message)

        bubble = QRect(
            msg_rect.left() - _PAD,
            msg_rect.top() - _PAD,
            msg_rect.width() + 2 * _PAD,
            msg_rect.height() + 2 * _PAD
        )

        author_line_top = bubble.bottom() + _PAD
        author_line = f"{item.author} {item.timestamp_str()}"
        author_line_x = bubble.x()
        if even_row:
            author_line_width = painter.fontMetrics().boundingRect(author_line).width()
            author_line_x = bubble.bottomRight().x() - author_line_width

        painter.drawRoundedRect(bubble, 8, 8)
        painter.drawText(msg_rect, Qt.TextFlag.TextWordWrap, message)
        painter.drawStaticText(author_line_x, author_line_top, QStaticText(author_line))
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        option.rect.setWidth(self.view.width())
        option.rect.setHeight(self.view.height())

        msg_rect = self.get_rects(option, index)
        bubble_size = QSize(msg_rect.width() + 2 * _PAD, msg_rect.height() + 2 * _PAD)

        font_metrics = QApplication.fontMetrics()
        sender_height = font_metrics.height() + 2 * _PAD

        item_size = QSize(bubble_size.width(), bubble_size.height() + sender_height)
        return item_size
