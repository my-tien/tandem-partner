from PySide6.QtCore import Qt, QModelIndex, QPoint, QRect, QSize
from PySide6.QtGui import QFontMetrics, QPainter, QPainterPath, QStaticText
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from chat_history.history_model import HistoryItem


_PAD = 8


class HistoryItemDelegate(QStyledItemDelegate):

    def get_painted_message(self, index: QModelIndex):
        item : HistoryItem = index.data()
        message = "\n\n".join((item.traditional, item.pinyin, item.english)).rstrip("\n")
        return message

    def get_rects(self, option, index: QModelIndex, message: str):
        self.initStyleOption(option, index)

        option_rect = option.rect
        font_metrics = QFontMetrics("TW-MOE-Std-Kai")

        max_width = option_rect.width() - 2 * _PAD
        text_width = min(font_metrics.boundingRect(message).width(), max_width)

        even_row = index.row() & 1 == 0
        x = option_rect.left() + _PAD
        y = option_rect.top() + _PAD
        alignment = Qt.AlignmentFlag.AlignLeft
        if even_row:
            alignment = Qt.AlignmentFlag.AlignRight
            x = option_rect.width() - text_width - _PAD
        
        msg_rect = font_metrics.boundingRect(
            x,
            y,
            text_width,
            0,
            alignment | Qt.AlignmentFlag.AlignTop,
            message
        )

        bubble = QRect(
            msg_rect.left() - _PAD,
            msg_rect.top() - _PAD,
            msg_rect.width() + _PAD,
            msg_rect.bottom() + _PAD
        )
        return msg_rect, bubble

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        item : HistoryItem = index.data()
        message = "\n\n".join((item.traditional, item.pinyin, item.english)).rstrip("\n")

        msg_rect, bubble = self.get_rects(option, index, message)
        
        even_row = index.row() & 1 == 0

        tail_x0 = bubble.topLeft().x() - _PAD
        tail_y0 = bubble.bottomRight().y()

        author_line_top = bubble.bottom() + _PAD
        author_line = f"{item.author} {item.timestamp_str()}"
        author_line_x = bubble.x()
        if even_row:
            author_line_width = painter.fontMetrics().boundingRect(author_line).width()
            author_line_x = bubble.bottomRight().x() - author_line_width

        painter.save()
        painter.drawRoundedRect(bubble, 8, 8)
        tail_path = QPainterPath(startPoint=QPoint(tail_x0, tail_y0))
        painter.drawText(msg_rect, message)
        painter.drawStaticText(author_line_x, author_line_top, QStaticText(author_line))

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        message = self.get_painted_message(index)
        _, bubble = self.get_rects(option, index, message)

        font_metrics = QFontMetrics("Arial")
        sender_height = font_metrics.height() + _PAD
        item_size = QSize(bubble.width(), bubble.height() + sender_height + _PAD)
        return item_size
