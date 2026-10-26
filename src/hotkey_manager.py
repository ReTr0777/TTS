import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

class HotkeyManager(QObject):
    triggered = pyqtSignal()

    def __init__(self, hotkey_str: str = "ctrl+space"):
        super().__init__()
        self.current_hotkey = hotkey_str
        self._hooked = False
        self.start()

    def start(self):
        self.register(self.current_hotkey)

    def register(self, hotkey_str: str):
        if not hotkey_str:
            return
        try:
            self.unregister()
            # suppress=True prevents the trigger hotkey (like Space in Ctrl+Space) from bleeding into games
            keyboard.add_hotkey(hotkey_str, self._on_hotkey_pressed, suppress=True)
            self.current_hotkey = hotkey_str
            self._hooked = True
            print(f"[HotkeyManager] Registered global hotkey (suppress=True): {hotkey_str}")
        except Exception as e:
            print(f"[HotkeyManager] Failed with suppress=True: {e}. Trying fallback...")
            try:
                keyboard.add_hotkey(hotkey_str, self._on_hotkey_pressed, suppress=False)
                self.current_hotkey = hotkey_str
                self._hooked = True
                print(f"[HotkeyManager] Registered global hotkey (fallback): {hotkey_str}")
            except Exception as e2:
                print(f"[HotkeyManager] Failed to register hotkey '{hotkey_str}': {e2}")

    def unregister(self):
        if self._hooked and self.current_hotkey:
            try:
                keyboard.remove_hotkey(self.current_hotkey)
            except Exception:
                pass
            self._hooked = False

    def _on_hotkey_pressed(self):
        self.triggered.emit()

    def stop(self):
        self.unregister()
