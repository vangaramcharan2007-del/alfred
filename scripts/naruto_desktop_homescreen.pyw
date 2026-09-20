import os
import sys
import ctypes
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(PROJECT_ROOT, "newtab", "index.html")

def main():
    app = QApplication(sys.argv)
    screen = QApplication.primaryScreen().geometry()
    
    view = QWebEngineView()
    settings = view.settings()
    settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
    settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
    settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
    settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
    settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
    
    # Stay on bottom: behind normal apps, pinned directly to the desktop
    view.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint | Qt.Tool)
    view.setAttribute(Qt.WA_TranslucentBackground)
    view.setGeometry(screen)
    
    url = QUrl.fromLocalFile(os.path.abspath(HTML_PATH))
    view.setUrl(url)
    view.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
