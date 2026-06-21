from __future__ import annotations

from collections import deque

from PySide6.QtCore import QPoint, QRect, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QApplication, QWidget


class WaveOverlay(QWidget):
    close_requested = Signal()
    stop_requested = Signal()
    pause_requested = Signal()

    def __init__(self, fps: int = 30):
        super().__init__()
        self.levels = deque([0.0] * 80, maxlen=80)
        self.status = "Ready"
        self.state = "idle"
        self.fps = max(1, fps)
        self._dragging = False
        self._drag_offset = QPoint()
        self._has_custom_position = False
        self._closed_by_user = False

        self.setFixedSize(520, 132)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)

    def show_status(self, text: str) -> None:
        if self._closed_by_user:
            return

        self.status = text
        if not self._has_custom_position:
            self._move_bottom_center()
        self.show()
        self.raise_()
        if not self.timer.isActive():
            self.timer.start(round(1000 / self.fps))

    def set_state(self, state: str) -> None:
        self.state = state
        self.update()

    def hide_overlay(self) -> None:
        self.timer.stop()
        self.hide()

    def push_level(self, value: float) -> None:
        self.levels.append(max(0.0, min(1.0, value)))

    def reset_user_close(self) -> None:
        self._closed_by_user = False

    def _move_bottom_center(self) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + (screen.width() - self.width()) // 2
        y = screen.y() + screen.height() - self.height() - 80
        self.move(x, y)

    def _close_rect(self) -> QRect:
        return QRect(self.width() - 44, 18, 24, 24)

    def _stop_rect(self) -> QRect:
        return QRect(self.width() - 116, 92, 88, 28)

    def _pause_rect(self) -> QRect:
        return QRect(self.width() - 220, 92, 96, 28)

    def _controls_visible(self) -> bool:
        return self.state in {"recording", "paused"}

    def _global_position(self, event) -> QPoint:
        if hasattr(event, "globalPosition"):
            return event.globalPosition().toPoint()
        return event.globalPos()

    def mousePressEvent(self, event) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return

        if self._close_rect().contains(event.position().toPoint()):
            self._closed_by_user = True
            self.hide_overlay()
            self.close_requested.emit()
            event.accept()
            return

        if self._controls_visible():
            local_position = event.position().toPoint()
            if self._stop_rect().contains(local_position):
                self.stop_requested.emit()
                event.accept()
                return
            if self._pause_rect().contains(local_position):
                self.pause_requested.emit()
                event.accept()
                return

        self._dragging = True
        self._drag_offset = self._global_position(event) - self.frameGeometry().topLeft()
        event.accept()

    def mouseMoveEvent(self, event) -> None:
        if not self._dragging:
            super().mouseMoveEvent(event)
            return

        self.move(self._clamped_position(self._global_position(event) - self._drag_offset))
        self._has_custom_position = True
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _clamped_position(self, position: QPoint) -> QPoint:
        screen = QApplication.screenAt(position) or QApplication.primaryScreen()
        geometry = screen.availableGeometry()
        x = min(max(position.x(), geometry.left()), geometry.right() - self.width() + 1)
        y = min(max(position.y(), geometry.top()), geometry.bottom() - self.height() + 1)
        return QPoint(x, y)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(14, 18, 26, 230))
        painter.drawRoundedRect(rect, 20, 20)

        painter.setPen(QColor(236, 240, 248, 238))
        status_text = painter.fontMetrics().elidedText(
            self.status,
            Qt.TextElideMode.ElideRight,
            self.width() - 96,
        )
        painter.drawText(28, 32, status_text)

        close_rect = self._close_rect()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(35, 42, 55, 210))
        painter.drawEllipse(close_rect)

        close_pen = QPen(QColor(236, 240, 248, 230))
        close_pen.setWidth(2)
        painter.setPen(close_pen)
        painter.drawLine(close_rect.left() + 8, close_rect.top() + 8, close_rect.right() - 7, close_rect.bottom() - 7)
        painter.drawLine(close_rect.right() - 7, close_rect.top() + 8, close_rect.left() + 8, close_rect.bottom() - 7)

        wave_left = 28
        wave_top = 48
        wave_width = self.width() - 56
        wave_height = 32
        levels = list(self.levels)
        if not levels:
            return

        bar_gap = 2
        bar_width = max(2, int((wave_width / len(levels)) - bar_gap))
        pen = QPen(QColor(92, 218, 255, 232))
        pen.setWidth(bar_width)
        painter.setPen(pen)
        center_y = wave_top + wave_height / 2

        for index, level in enumerate(levels):
            x = wave_left + index * (bar_width + bar_gap)
            height = 4 + level * wave_height
            painter.drawLine(
                int(x),
                int(center_y - height / 2),
                int(x),
                int(center_y + height / 2),
            )

        if self._controls_visible():
            self._draw_button(painter, self._pause_rect(), "Resume" if self.state == "paused" else "Pause")
            self._draw_button(painter, self._stop_rect(), "Stop")

    def _draw_button(self, painter: QPainter, rect: QRect, text: str) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(35, 42, 55, 230))
        painter.drawRoundedRect(rect, 8, 8)

        painter.setPen(QColor(236, 240, 248, 240))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)
