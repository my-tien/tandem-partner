from PySide6.QtCore import Qt, QModelIndex, QRect, QSize
from PySide6.QtGui import QFont, QFontMetrics, QPainter, QStaticText
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from chat_history.history_model import HistoryItem


_PAD = 8


class HistoryItemDelegate(QStyledItemDelegate):
    def get_painted_message(self, index: QModelIndex):
        item : HistoryItem = index.data()
        message = "\n\n".join((item.traditional, item.pinyin, item.english)).rstrip("\n")
        return message

    def get_rects(self, option: QStyleOptionViewItem, index: QModelIndex):
        self.initStyleOption(option, index)
        message = self.get_painted_message(index)

        option_rect = option.rect
        font_metrics = QFontMetrics(QFont().defaultFamily())
        max_width = option_rect.width() - 2 * _PAD
        text_width = min(font_metrics.boundingRect(message).width(), max_width)

        even_row = index.row() & 1 == 0
        x = option_rect.left() + _PAD
        y = option_rect.top() + _PAD
        alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        if even_row:
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop
            x = option_rect.left() + option_rect.width() - text_width - 2 * _PAD

        height = font_metrics.boundingRect(
            0, 0, text_width, 0, alignment, self.get_painted_message(index)
        ).height()

        msg_rect = QRect(x, y, text_width, height)

        return msg_rect

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item : HistoryItem = index.data()
        message = self.get_painted_message(index)
        msg_rect = self.get_rects(option, index)
        
        even_row = index.row() & 1 == 0

        painter.save()
        alignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        if even_row:
            alignment = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop

        msg_rect = painter.boundingRect(msg_rect, alignment, message)
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
        painter.drawText(msg_rect, 0, message)
        painter.drawStaticText(author_line_x, author_line_top, QStaticText(author_line))

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        font_metrics = QFontMetrics(QFont(QFont().defaultFamily(), 18))
        msg_rect = self.get_rects(option, index)
        bubble_size = QSize(msg_rect.width() + 2 * _PAD, msg_rect.height() + 2 * _PAD)
        sender_height = font_metrics.height() + 2 * _PAD
        item_size = QSize(bubble_size.width(), bubble_size.height() + sender_height)
        return item_size
