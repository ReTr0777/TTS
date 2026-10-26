import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent.parent / "config.json"

DEFAULT_CONFIG = {
    "hotkey": "ctrl+space",
    "routing_mode": "discord_only", # "discord_only", "all_mics", "custom"
    "discord_output_device": "",
    "virtual_mic_device": "",
    "monitor_device": "",
    "auto_hide_on_speak": True,
    "play_monitor": True,
    "tts_engine": "edge-tts",
    "voice": "en-US-ChristopherNeural",
    "rate": "+0%",
    "pitch": "+0Hz",
    "volume_mic": 1.0,
    "volume_monitor": 0.8,
    "mic_passthrough_enabled": False,
    "physical_mic_device": "",
    "history": [],
    "quick_phrases": [
        "Hello everyone!",
        "Be right back, one minute.",
        "Good game!",
        "Can you hear me alright?",
        "Yes, absolutely.",
        "No, thank you."
    ]
}

class ConfigManager:
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self.config.update(loaded)
            except Exception as e:
                print(f"[Config] Error loading config: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def add_to_history(self, text: str):
        if not text or not text.strip():
            return
        text = text.strip()
        history = self.config.get("history", [])
        if text in history:
            history.remove(text)
        history.insert(0, text)
        self.config["history"] = history[:50]
        self.save()

# Global singleton
config = ConfigManager()
