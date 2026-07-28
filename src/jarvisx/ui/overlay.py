import sys
import math
import struct
import socket
import threading
import numpy as np

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush

try:
    import pyaudio
    HAS_AUDIO = True
except ImportError:
    HAS_AUDIO = False


class UdpListener(QThread):
    command_received = pyqtSignal(str)

    def __init__(self, port=8766):
        super().__init__()
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("127.0.0.1", self.port))
        self.running = True

    def run(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(1024)
                if data:
                    self.command_received.emit(data.decode("utf-8").strip())
            except Exception:
                pass


class WaveformOverlay(QWidget):
    def __init__(self):
        super().__init__()
        
        # Window settings for transparent click-through overlay
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.Tool | 
            Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Position at top right
        screen = QApplication.primaryScreen().geometry()
        self.width = 300
        self.height = 150
        # 50px margin from top right
        self.setGeometry(screen.width() - self.width - 50, 50, self.width, self.height)

        # State
        self.color = QColor(0, 240, 255) # Default Friday Cyan
        self.amplitudes = [0.1] * 5
        self.phase = 0.0

        # Audio Setup
        self.audio = None
        self.stream = None
        if HAS_AUDIO:
            self.init_audio()

        # Animation timer (30 FPS)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(33)

        # UDP Listener for commands
        self.udp = UdpListener()
        self.udp.command_received.connect(self.handle_command)
        self.udp.start()

    def init_audio(self):
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=1024
            )
        except Exception as e:
            print(f"Overlay audio init failed: {e}")
            HAS_AUDIO = False

    def handle_command(self, cmd):
        # Expected format: "COLOR #RRGGBB" or "COLOR friday" / "COLOR alfred"
        parts = cmd.split(" ")
        if len(parts) >= 2 and parts[0] == "COLOR":
            val = parts[1].lower()
            if val == "friday":
                self.color = QColor(0, 240, 255) # Cyan
            elif val == "alfred":
                self.color = QColor(0, 150, 255) # Blue
            elif val == "edith":
                self.color = QColor(255, 165, 0) # Orange
            elif val.startswith("#"):
                self.color = QColor(val)

    def update_frame(self):
        self.phase += 0.2
        
        if HAS_AUDIO and self.stream and self.stream.is_active():
            try:
                # Non-blocking read
                if self.stream.get_read_available() > 0:
                    data = self.stream.read(1024, exception_on_overflow=False)
                    # Convert to numpy array
                    samples = np.frombuffer(data, dtype=np.int16)
                    # Calculate volume (RMS)
                    rms = np.sqrt(np.mean(samples**2))
                    # Normalize to 0-1 (roughly, max int16 is 32768)
                    vol = min(1.0, rms / 4000.0) 
                    
                    # Smoothly update amplitudes
                    target = max(0.1, vol)
                    for i in range(5):
                        # Add some variation per bar
                        var_target = target * (0.8 + 0.4 * math.sin(self.phase + i))
                        self.amplitudes[i] = self.amplitudes[i] * 0.7 + var_target * 0.3
            except Exception:
                pass
        else:
            # Idle animation if no audio
            for i in range(5):
                self.amplitudes[i] = 0.2 + 0.1 * math.sin(self.phase + i * 0.5)

        self.update() # Trigger paintEvent

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw a subtle background glow for the whole widget
        # gradient = QRadialGradient(self.width/2, self.height/2, self.width/2)
        # c = QColor(self.color)
        # c.setAlpha(20)
        # gradient.setColorAt(0, c)
        # gradient.setColorAt(1, QColor(0,0,0,0))
        # painter.fillRect(0, 0, self.width, self.height, QBrush(gradient))

        # Draw waveform bars
        center_x = self.width / 2
        center_y = self.height / 2
        bar_width = 8
        spacing = 16
        
        # 5 bars
        total_width = 5 * bar_width + 4 * spacing
        start_x = center_x - (total_width / 2) + (bar_width / 2)

        pen = QPen(self.color)
        pen.setWidth(bar_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        max_h = self.height * 0.6

        for i in range(5):
            x = start_x + i * (bar_width + spacing)
            h = self.amplitudes[i] * max_h
            # Ensure minimum height
            h = max(8, h)
            
            painter.drawLine(int(x), int(center_y - h/2), int(x), int(center_y + h/2))

    def closeEvent(self, event):
        self.udp.running = False
        if HAS_AUDIO and self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    overlay = WaveformOverlay()
    overlay.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
