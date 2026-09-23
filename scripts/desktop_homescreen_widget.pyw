import os
import sys
import time
from datetime import datetime
import ctypes
from ctypes import wintypes

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette

# Win32 Constants for Click-Through and Desktop integration
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080

class DesktopClockWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.apply_click_through()

    def init_ui(self):
        # Frameless, transparent background, tool window (no taskbar item), stays on bottom
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnBottomHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)

        # Main Layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(4)
        layout.setContentsMargins(40, 30, 40, 30)

        # 1. Greeting Label
        self.greeting_label = QLabel("GOOD EVENING, BOSS")
        self.greeting_label.setAlignment(Qt.AlignCenter)
        self.greeting_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.75);
            font-size: 15px;
            font-weight: 500;
            letter-spacing: 5px;
            font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
        """)

        # 2. Digital Clock Label
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 88px;
            font-weight: 200;
            letter-spacing: -2px;
            font-family: 'Segoe UI Light', 'SF Pro Display', Arial, sans-serif;
        """)

        # 3. Date Label
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.85);
            font-size: 18px;
            font-weight: 400;
            letter-spacing: 2px;
            font-family: 'Segoe UI', 'SF Pro Display', Arial, sans-serif;
        """)

        layout.addWidget(self.greeting_label)
        layout.addWidget(self.time_label)
        layout.addWidget(self.date_label)
        self.setLayout(layout)

        # Background card styling
        self.setStyleSheet("""
            DesktopClockWidget {
                background: rgba(15, 18, 25, 0.45);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 24px;
            }
        """)

        # Update time immediately and start timer
        self.update_time()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # Position widget comfortably on primary screen (Top-Center of Desktop)
        screen = QApplication.primaryScreen().geometry()
        widget_w = 460
        widget_h = 240
        pos_x = (screen.width() - widget_w) // 2
        pos_y = int(screen.height() * 0.12) # 12% down from top
        self.setGeometry(pos_x, pos_y, widget_w, widget_h)

    def update_time(self):
        now = datetime.now()
        # 12-hour format with AM/PM
        self.time_label.setText(now.strftime("%I:%M %p"))
        # Day, Month Date
        self.date_label.setText(now.strftime("%A, %B %d").upper())

        hour = now.hour
        if 5 <= hour < 12:
            greet = "GOOD MORNING, BOSS"
        elif 12 <= hour < 17:
            greet = "GOOD AFTERNOON, BOSS"
        elif 17 <= hour < 22:
            greet = "GOOD EVENING, BOSS"
        else:
            greet = "NIGHT PROTOCOL, BOSS"
        self.greeting_label.setText(greet)

    def apply_click_through(self):
        """Enable click-through so user can click/drag desktop icons freely underneath."""
        try:
            hwnd = int(self.winId())
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW)
        except Exception as e:
            print(f"Click-through error: {e}")

def main():
    app = QApplication(sys.argv)
    widget = DesktopClockWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
