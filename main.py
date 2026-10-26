import sys
import os
from pathlib import Path

# Ensure root directory is on python path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from PyQt6.QtWidgets import QApplication, QSystemTrayIcon
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

from src.config import config
from src.audio_engine import audio_engine
from src.hotkey_manager import HotkeyManager
from src.ui.bubble_window import TextBubbleWindow
from src.ui.settings_dialog import SettingsDialog
from src.ui.tray_icon import TrayIcon, ICON_PATH

def main():
    # Windows high-DPI scaling
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    app.setQuitOnLastWindowClosed(False) # Essential for tray-based apps
    app.setApplicationName("QuickTTS")
    app.setApplicationDisplayName("QuickTTS - Mic TTS Bot")

    # Set App Icon
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    # Auto-detect default audio endpoints on first run
    if not config.get("discord_output_device") or not config.get("virtual_mic_device") or not config.get("monitor_device"):
        d_auto, a_auto, m_auto = audio_engine.auto_detect_devices()
        outputs = audio_engine.list_output_devices()
        
        if d_auto is not None and not config.get("discord_output_device"):
            for d in outputs:
                if d["id"] == d_auto:
                    config.set("discord_output_device", d["full_label"])
                    print(f"[Init] Auto-selected Discord Output: {d['full_label']}")
                    break

        if a_auto is not None and not config.get("virtual_mic_device"):
            for d in outputs:
                if d["id"] == a_auto:
                    config.set("virtual_mic_device", d["full_label"])
                    print(f"[Init] Auto-selected Virtual Mic: {d['full_label']}")
                    break

        if m_auto is not None and not config.get("monitor_device"):
            for d in outputs:
                if d["id"] == m_auto:
                    config.set("monitor_device", d["full_label"])
                    print(f"[Init] Auto-selected Monitor Headphone: {d['full_label']}")
                    break

    # Initialize components
    bubble_window = TextBubbleWindow()
    settings_dialog = SettingsDialog()
    tray_icon = TrayIcon()
    tray_icon.show()

    current_hotkey = config.get("hotkey", "ctrl+space")
    hotkey_manager = HotkeyManager(current_hotkey)

    # Wire signals
    hotkey_manager.triggered.connect(bubble_window.show_and_focus)
    tray_icon.openBubbleRequested.connect(bubble_window.show_and_focus)
    tray_icon.openSettingsRequested.connect(settings_dialog.exec)
    bubble_window.openSettingsRequested.connect(settings_dialog.exec)

    def on_hotkey_changed(new_hotkey: str):
        hotkey_manager.register(new_hotkey)
        tray_icon.update_hotkey_label(new_hotkey)

    settings_dialog.hotkeyChanged.connect(on_hotkey_changed)

    def on_exit():
        hotkey_manager.stop()
        audio_engine.stop()
        tray_icon.hide()
        app.quit()

    tray_icon.exitRequested.connect(on_exit)

    # Welcome notification
    hk_disp = current_hotkey.upper()
    tray_icon.showMessage(
        "QuickTTS Ready!",
        f"Press {hk_disp} anytime to speak through your microphone.",
        QIcon(str(ICON_PATH)) if ICON_PATH.exists() else QSystemTrayIcon.MessageIcon.Information,
        4000
    )

    print(f"==================================================")
    print(f" QuickTTS - Mic Speech Bot Running")
    print(f" Press {hk_disp} to open the text bubble")
    print(f" Right-click the system tray icon for settings")
    print(f"==================================================")

    # Show bubble on launch so user can see it right away!
    bubble_window.show_and_focus()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
