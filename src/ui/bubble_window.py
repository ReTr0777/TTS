import sys
import ctypes
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtWidgets import (
    QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QLabel, QGraphicsDropShadowEffect, QMenu, QApplication
)
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush, QPen, QAction

from src.config import config
from src.audio_engine import audio_engine, POPULAR_VOICES
from src.ui.theme import BUBBLE_STYLE, COLORS

class WaveformVisualizer(QWidget):
    """Animated mini waveform that pulses when TTS is speaking."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 20)
        self._bars = [0.2, 0.4, 0.7, 0.3]
        self._step = 0
        self._animating = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate_step)
        
    def set_animating(self, active: bool):
        self._animating = active
        if active:
            if not self.timer.isActive():
                self.timer.start(80)
        else:
            self.timer.stop()
            self._bars = [0.2, 0.4, 0.7, 0.3]
            self.update()

    def _animate_step(self):
        self._step += 1
        import math
        self._bars = [
            0.2 + 0.6 * abs(math.sin(self._step * 0.4)),
            0.2 + 0.7 * abs(math.sin(self._step * 0.4 + 1.0)),
            0.2 + 0.8 * abs(math.sin(self._step * 0.4 + 2.0)),
            0.2 + 0.5 * abs(math.sin(self._step * 0.4 + 3.0)),
        ]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bar_width = 3.2
        spacing = 3.5
        h = self.height()
        
        color = QColor(COLORS["accent_cyan"] if self._animating else COLORS["text_muted"])
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        
        for i, val in enumerate(self._bars):
            bar_h = max(3.5, val * h)
            x = i * (bar_width + spacing) + 2
            y = (h - bar_h) / 2
            painter.drawRoundedRect(int(x), int(y), int(bar_width), int(bar_h), 2, 2)

class BubbleLineEdit(QLineEdit):
    """Custom QLineEdit with up/down history and Enter/Esc hooks."""
    enterPressed = pyqtSignal()
    escPressed = pyqtSignal()
    upPressed = pyqtSignal()
    downPressed = pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.enterPressed.emit()
        elif event.key() == Qt.Key.Key_Escape:
            self.escPressed.emit()
        elif event.key() == Qt.Key.Key_Up:
            self.upPressed.emit()
        elif event.key() == Qt.Key.Key_Down:
            self.downPressed.emit()
        else:
            super().keyPressEvent(event)

class TextBubbleWindow(QWidget):
    openSettingsRequested = pyqtSignal()

    def __init__(self):
        super().__init__()
        # Use top-level Frameless + WindowStaysOnTop.
        # DO NOT use Qt.WindowType.Tool, because Tool windows fail to steal foreground focus from games!
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setStyleSheet(BUBBLE_STYLE)
        
        self.history_index = -1
        self._current_typed = ""
        self._previous_window_hwnd = None
        
        self._init_ui()
        self._setup_connections()

    def _init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)

        # Bubble container
        self.container = QFrame(self)
        self.container.setObjectName("BubbleContainer")
        self.container.setFixedHeight(58)
        
        # Soft Drop shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 0, 0, 190))
        shadow.setOffset(0, 6)
        self.container.setGraphicsEffect(shadow)

        # Inner layout
        layout = QHBoxLayout(self.container)
        layout.setContentsMargins(14, 8, 14, 8)
        layout.setSpacing(8)

        # Glowing Mic Icon
        self.mic_icon = QLabel("🎙", self.container)
        self.mic_icon.setObjectName("MicIcon")
        layout.addWidget(self.mic_icon)

        # Text input
        self.input_field = BubbleLineEdit(self.container)
        self.input_field.setObjectName("TextInput")
        self.input_field.setPlaceholderText("Type to speak into Discord mic... (Enter = Speak, Esc = Cancel)")
        layout.addWidget(self.input_field, stretch=1)

        # Waveform indicator
        self.waveform = WaveformVisualizer(self.container)
        layout.addWidget(self.waveform)

        # Target badge (Discord-Only vs All Mics)
        self.target_badge = QPushButton(self.container)
        self.target_badge.setObjectName("VoiceChip")
        self.target_badge.setStyleSheet("""
            QPushButton#VoiceChip {
                background-color: #1A1F30;
                color: #5865F2; /* Discord Blurple */
                border: 1px solid #333C5C;
                font-weight: bold;
            }
            QPushButton#VoiceChip:hover {
                background-color: #252C44;
                border-color: #5865F2;
                color: #7983F5;
            }
        """)
        self.target_badge.setToolTip("Audio Output Destination (Click to change)")
        self.target_badge.clicked.connect(self.openSettingsRequested.emit)
        layout.addWidget(self.target_badge)

        # Voice badge chip
        self.voice_chip = QPushButton(self.container)
        self.voice_chip.setObjectName("VoiceChip")
        self.voice_chip.clicked.connect(self._show_voice_menu)
        layout.addWidget(self.voice_chip)

        # Quick phrases button
        self.phrases_btn = QPushButton("💬", self.container)
        self.phrases_btn.setObjectName("IconButton")
        self.phrases_btn.setToolTip("Quick Phrases")
        self.phrases_btn.setFixedSize(28, 28)
        self.phrases_btn.clicked.connect(self._show_phrases_menu)
        layout.addWidget(self.phrases_btn)

        # Settings gear button
        self.settings_btn = QPushButton("⚙", self.container)
        self.settings_btn.setObjectName("IconButton")
        self.settings_btn.setToolTip("Audio Routing & Settings")
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.clicked.connect(self.openSettingsRequested.emit)
        layout.addWidget(self.settings_btn)

        # Close button
        self.close_btn = QPushButton("✕", self.container)
        self.close_btn.setObjectName("IconButton")
        self.close_btn.setToolTip("Hide (Esc)")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.clicked.connect(self.hide_bubble)
        layout.addWidget(self.close_btn)

        self.main_layout.addWidget(self.container)
        self.setFixedWidth(730)
        self._update_badges()

    def _setup_connections(self):
        self.input_field.enterPressed.connect(self.submit_text)
        self.input_field.escPressed.connect(self.hide_bubble)
        self.input_field.upPressed.connect(self._history_up)
        self.input_field.downPressed.connect(self._history_down)
        audio_engine.on_state_change = self._on_audio_state_change

    def _on_audio_state_change(self, is_speaking: bool):
        QTimer.singleShot(0, lambda: self.waveform.set_animating(is_speaking))

    def _update_badges(self):
        # Update Voice
        current_voice_id = config.get("voice", "en-US-ChristopherNeural")
        name = current_voice_id.split("-")[-1].replace("Neural", "")
        self.voice_chip.setText(f"🗣 {name}")

        # Update Target Routing Badge
        mode = config.get("routing_mode", "discord_only")
        if mode == "discord_only":
            self.target_badge.setText("🎯 Discord-Only")
        elif mode == "all_mics":
            self.target_badge.setText("🎙 All-Mics")
        else:
            self.target_badge.setText("🔊 Custom")

    def _show_voice_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161926;
                color: #F8FAFC;
                border: 1px solid #2F3754;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 14px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #6366F1;
                color: #FFFFFF;
            }
        """)
        
        current_voice = config.get("voice", "")
        for v in POPULAR_VOICES[:10]:
            action = QAction(v["name"], self)
            action.setCheckable(True)
            action.setChecked(v["id"] == current_voice)
            action.triggered.connect(lambda checked, vid=v["id"]: self._set_quick_voice(vid))
            menu.addAction(action)
            
        menu.addSeparator()
        more_act = QAction("⚙ Voice & Audio Settings...", self)
        more_act.triggered.connect(self.openSettingsRequested.emit)
        menu.addAction(more_act)
        
        menu.exec(self.voice_chip.mapToGlobal(self.voice_chip.rect().bottomLeft()))

    def _show_phrases_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #161926;
                color: #F8FAFC;
                border: 1px solid #2F3754;
                border-radius: 8px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 14px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #6366F1;
                color: #FFFFFF;
            }
        """)
        
        phrases = config.get("quick_phrases", [])
        if not phrases:
            action = QAction("No quick phrases configured", self)
            action.setEnabled(False)
            menu.addAction(action)
        else:
            for phrase in phrases:
                action = QAction(f"💬 {phrase}", self)
                action.triggered.connect(lambda checked, p=phrase: self._speak_phrase(p))
                menu.addAction(action)
                
        menu.exec(self.phrases_btn.mapToGlobal(self.phrases_btn.rect().bottomLeft()))

    def _speak_phrase(self, phrase: str):
        self.input_field.setText(phrase)
        self.submit_text()

    def _set_quick_voice(self, voice_id: str):
        config.set("voice", voice_id)
        self._update_badges()

    def _history_up(self):
        history = config.get("history", [])
        if not history:
            return
        if self.history_index == -1:
            self._current_typed = self.input_field.text()
            self.history_index = 0
        elif self.history_index < len(history) - 1:
            self.history_index += 1
            
        if 0 <= self.history_index < len(history):
            self.input_field.setText(history[self.history_index])

    def _history_down(self):
        history = config.get("history", [])
        if not history or self.history_index == -1:
            return
        self.history_index -= 1
        if self.history_index >= 0:
            self.input_field.setText(history[self.history_index])
        else:
            self.history_index = -1
            self.input_field.setText(self._current_typed)

    def submit_text(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        config.add_to_history(text)
        self.history_index = -1
        self._current_typed = ""
        
        # Speak through configured microphone routing (Discord-Only or All-Mics)
        audio_engine.speak(text)
        
        self.input_field.clear()
        
        if config.get("auto_hide_on_speak", True):
            self.hide_bubble()

    def _force_activate(self):
        """Forces Windows OS foreground keyboard focus to this bubble, stripping it from games."""
        try:
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            fg_hwnd = user32.GetForegroundWindow()
            my_hwnd = int(self.winId())
            
            # Record previous window so we return focus to game on hide
            if fg_hwnd != my_hwnd and fg_hwnd != 0:
                self._previous_window_hwnd = fg_hwnd
                
            current_thread_id = kernel32.GetCurrentThreadId()
            fg_thread_id = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0

            # Allow foreground window switch
            user32.AllowSetForegroundWindow(-1) # ASFW_ANY

            # Attach thread input to bypass foreground lock from game
            if fg_thread_id and fg_thread_id != current_thread_id:
                user32.AttachThreadInput(fg_thread_id, current_thread_id, True)
                user32.ShowWindow(my_hwnd, 5) # SW_SHOW
                user32.BringWindowToTop(my_hwnd)
                user32.SetForegroundWindow(my_hwnd)
                user32.SetActiveWindow(my_hwnd)
                user32.SwitchToThisWindow(my_hwnd, True)
                user32.AttachThreadInput(fg_thread_id, current_thread_id, False)
            else:
                user32.ShowWindow(my_hwnd, 5)
                user32.BringWindowToTop(my_hwnd)
                user32.SetForegroundWindow(my_hwnd)
                user32.SetActiveWindow(my_hwnd)
                user32.SwitchToThisWindow(my_hwnd, True)
        except Exception as e:
            print(f"[BubbleWindow] Error forcing foreground focus: {e}")

    def _restore_previous_focus(self):
        """Restores focus seamlessly back to the game window."""
        if self._previous_window_hwnd:
            try:
                ctypes.windll.user32.SetForegroundWindow(self._previous_window_hwnd)
            except Exception:
                pass
            self._previous_window_hwnd = None

    def show_and_focus(self):
        """Displays bubble, immediately captures typing focus, and prevents game movement."""
        # Toggle behavior: if already visible and active, pressing hotkey hides it and returns to game
        if self.isVisible() and self.isActiveWindow():
            self.hide_bubble()
            return

        self._update_badges()
        
        # Position in top-center of screen
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = int(screen.height() * 0.22)
        self.move(x, y)
        
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Windows API force focus from game
        self._force_activate()
        
        # Instantly focus text field and select text
        self.input_field.setFocus(Qt.FocusReason.OtherFocusReason)
        self.input_field.selectAll()

    def hide_bubble(self):
        self.hide()
        self.history_index = -1
        # Seamlessly return focus to the game window
        self._restore_previous_focus()
