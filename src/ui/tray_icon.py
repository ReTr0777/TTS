import os
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import pyqtSignal

from src.config import config
from src.audio_engine import audio_engine

ASSETS_DIR = Path(__file__).resolve().parent.parent.parent / "assets"
ICON_PATH = ASSETS_DIR / "icon.png"

def create_fallback_icon() -> QIcon:
    """Generates an in-memory modern glowing icon if icon.png is missing."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Background circle
    painter.setBrush(QBrush(QColor(99, 102, 241)))
    painter.setPen(QColor(139, 92, 246))
    painter.drawRoundedRect(4, 4, 56, 56, 16, 16)
    
    # Inner mic shape
    painter.setBrush(QBrush(QColor(255, 255, 255)))
    painter.drawRoundedRect(24, 14, 16, 26, 8, 8)
    painter.end()
    return QIcon(pixmap)

class TrayIcon(QSystemTrayIcon):
    openBubbleRequested = pyqtSignal()
    openSettingsRequested = pyqtSignal()
    exitRequested = pyqtSignal()

    def __init__(self, parent=None):
        if ICON_PATH.exists():
            icon = QIcon(str(ICON_PATH))
        else:
            icon = create_fallback_icon()
            
        super().__init__(icon, parent)
        self.setToolTip("QuickTTS - Mic TTS Bot")
        self._init_menu()
        self.activated.connect(self._on_activated)

    def _init_menu(self):
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #161926;
                color: #F8FAFC;
                border: 1px solid #2F3754;
                border-radius: 8px;
                padding: 4px;
                font-family: 'Segoe UI', system-ui, sans-serif;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #6366F1;
                color: #FFFFFF;
            }
        """)

        hk = config.get("hotkey", "ctrl+space").upper()
        self.open_action = QAction(f"💬 Open Text Bubble ({hk})", self)
        self.open_action.triggered.connect(self.openBubbleRequested.emit)
        menu.addAction(self.open_action)

        menu.addSeparator()

        settings_action = QAction("⚙ Settings & Audio Routing...", self)
        settings_action.triggered.connect(self.openSettingsRequested.emit)
        menu.addAction(settings_action)

        stop_action = QAction("🛑 Stop Speaking", self)
        stop_action.triggered.connect(audio_engine.stop)
        menu.addAction(stop_action)

        test_action = QAction("🔊 Test Audio Output", self)
        test_action.triggered.connect(lambda: audio_engine.speak("QuickTTS audio test."))
        menu.addAction(test_action)

        menu.addSeparator()

        exit_action = QAction("❌ Exit QuickTTS", self)
        exit_action.triggered.connect(self.exitRequested.emit)
        menu.addAction(exit_action)

        self.setContextMenu(menu)

    def update_hotkey_label(self, new_hotkey: str):
        self.open_action.setText(f"💬 Open Text Bubble ({new_hotkey.upper()})")

    def _on_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.openBubbleRequested.emit()
