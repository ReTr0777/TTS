import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSlider, QCheckBox, QPushButton,
    QLineEdit, QListWidget, QGroupBox, QRadioButton, QButtonGroup,
    QInputDialog, QFrame
)
from PyQt6.QtGui import QIcon

from src.config import config
from src.audio_engine import audio_engine, POPULAR_VOICES
from src.ui.theme import SETTINGS_STYLE

class SettingsDialog(QDialog):
    hotkeyChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QuickTTS - Settings & Audio Routing")
        self.setMinimumSize(660, 560)
        self.setStyleSheet(SETTINGS_STYLE)

        self._init_ui()
        self._load_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(14)

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("QuickTTS Settings")
        title_label.setObjectName("title")
        title_label.setProperty("class", "title")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Tabs
        self.tabs = QTabWidget(self)
        self.tabs.addTab(self._create_audio_tab(), "🎙 Audio Routing")
        self.tabs.addTab(self._create_voice_tab(), "🗣 Voice & Speech")
        self.tabs.addTab(self._create_hotkey_tab(), "⌨ Keybind & Gaming")
        self.tabs.addTab(self._create_phrases_tab(), "💬 Quick Phrases")
        main_layout.addWidget(self.tabs)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save & Apply", self)
        self.save_btn.setProperty("class", "primary")
        self.save_btn.clicked.connect(self._save_settings)

        self.cancel_btn = QPushButton("Cancel", self)
        self.cancel_btn.setProperty("class", "secondary")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        main_layout.addLayout(btn_layout)

    def _create_audio_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # Routing Mode Selection Box
        mode_group = QGroupBox("🎯 Output Destination (Discord-Only vs All Mics)")
        mode_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        mode_layout = QVBoxLayout(mode_group)

        self.mode_btn_group = QButtonGroup(self)
        self.radio_discord = QRadioButton("Discord-Only Output (Recommended for Gamers)")
        self.radio_all_mics = QRadioButton("All-Mics Output (Discord + In-Game Voice Chat)")
        self.radio_custom = QRadioButton("Custom Output Device")

        self.mode_btn_group.addButton(self.radio_discord, 1)
        self.mode_btn_group.addButton(self.radio_all_mics, 2)
        self.mode_btn_group.addButton(self.radio_custom, 3)

        mode_layout.addWidget(self.radio_discord)
        discord_desc = QLabel("   • Only Discord will hear the TTS. In-game voice chat will NOT hear it!")
        discord_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        mode_layout.addWidget(discord_desc)

        mode_layout.addWidget(self.radio_all_mics)
        all_desc = QLabel("   • Broadcasts into your main mic stream so both Discord and games hear the bot.")
        all_desc.setStyleSheet("color: #94A3B8; font-size: 11px;")
        mode_layout.addWidget(all_desc)

        mode_layout.addWidget(self.radio_custom)
        layout.addWidget(mode_group)

        # Output Device Selector
        dev_group = QGroupBox("Audio Output Device")
        dev_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        dev_layout = QVBoxLayout(dev_group)

        dev_row = QHBoxLayout()
        self.out_combo = QComboBox()
        self.out_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        dev_row.addWidget(self.out_combo, stretch=1)

        self.detect_btn = QPushButton("Auto-Detect")
        self.detect_btn.setProperty("class", "secondary")
        self.detect_btn.clicked.connect(self._auto_detect_devices)
        dev_row.addWidget(self.detect_btn)

        self.install_cable_btn = QPushButton("⚡ Install Dedicated Cable")
        self.install_cable_btn.setProperty("class", "secondary")
        self.install_cable_btn.setToolTip("Install official VB-CABLE so Discord has its own dedicated 'CABLE Output' input")
        self.install_cable_btn.clicked.connect(self._install_dedicated_cable)
        dev_row.addWidget(self.install_cable_btn)

        self.test_mic_btn = QPushButton("Test Audio")
        self.test_mic_btn.setProperty("class", "secondary")
        self.test_mic_btn.clicked.connect(self._test_output)
        dev_row.addWidget(self.test_mic_btn)
        dev_layout.addLayout(dev_row)

        # Step-by-Step Discord Helper Callout Box
        help_box = QFrame()
        help_box.setStyleSheet("""
            QFrame {
                background-color: #121522;
                border: 1px solid #2F3754;
                border-left: 3px solid #5865F2; /* Discord blurple */
                border-radius: 6px;
                padding: 8px 12px;
            }
        """)
        hb_layout = QVBoxLayout(help_box)
        hb_layout.setContentsMargins(8, 8, 8, 8)
        hb_layout.setSpacing(4)

        hb_title = QLabel("🎮 How to select its own input in Discord (Active Right Now!):")
        hb_title.setStyleSheet("color: #7983F5; font-weight: bold; font-size: 13px;")
        hb_layout.addWidget(hb_title)

        hb_text = QLabel(
            "<b>🎯 Recommended Setup (Works RIGHT NOW — No Reboot & No Voicemeeter needed!):</b><br>"
            "1. In <b>Discord</b> (Voice & Video > Input Device): Look at the very top item in your screenshot:<br>"
            "   👉 Select <b>SteelSeries Sonar Virtual Audio Device (SteelSeries Sonar - Microphone)</b>.<br>"
            "2. In <b>QuickTTS</b>: Output Device is set to <b>SteelSeries Sonar - Microphone [Windows WASAPI]</b>.<br>"
            "3. In your <b>Game</b>: Keep your microphone as <b>Arctis Nova Pro Wireless</b>.<br><br>"
            "<i>✅ Result: Zero Voicemeeter required! Zero PC restart required! The TTS bot speaks directly into Discord on its own dedicated channel, and your game voice chat never hears it!</i>"
        )
        hb_text.setStyleSheet("color: #CBD5E1; font-size: 11px;")
        hb_layout.addWidget(hb_text)
        dev_layout.addWidget(help_box)

        # Output Volume
        vol_row = QHBoxLayout()
        vol_row.addWidget(QLabel("Output Volume:"))
        self.mic_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.mic_vol_slider.setRange(10, 150)
        self.mic_vol_slider.setValue(100)
        self.mic_vol_label = QLabel("100%")
        self.mic_vol_slider.valueChanged.connect(lambda v: self.mic_vol_label.setText(f"{v}%"))
        vol_row.addWidget(self.mic_vol_slider, stretch=1)
        vol_row.addWidget(self.mic_vol_label)
        dev_layout.addLayout(vol_row)

        layout.addWidget(dev_group)

        # Monitor Section
        mon_group = QGroupBox("Headphone Monitoring (Hear yourself speak)")
        mon_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        mon_layout = QVBoxLayout(mon_group)

        self.mon_enable_cb = QCheckBox("Enable Local Monitoring (Play TTS into your headphones simultaneously)")
        mon_layout.addWidget(self.mon_enable_cb)

        mon_row = QHBoxLayout()
        self.mon_combo = QComboBox()
        self.mon_combo.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        mon_row.addWidget(self.mon_combo, stretch=1)

        self.mon_test_btn = QPushButton("Test Headphones")
        self.mon_test_btn.setProperty("class", "secondary")
        self.mon_test_btn.clicked.connect(self._test_monitor_output)
        mon_row.addWidget(self.mon_test_btn)
        mon_layout.addLayout(mon_row)

        # Monitor Volume
        mon_vol_row = QHBoxLayout()
        mon_vol_row.addWidget(QLabel("Monitor Volume:"))
        self.mon_vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.mon_vol_slider.setRange(10, 100)
        self.mon_vol_slider.setValue(80)
        self.mon_vol_label = QLabel("80%")
        self.mon_vol_slider.valueChanged.connect(lambda v: self.mon_vol_label.setText(f"{v}%"))
        mon_vol_row.addWidget(self.mon_vol_slider, stretch=1)
        mon_vol_row.addWidget(self.mon_vol_label)
        mon_layout.addLayout(mon_vol_row)

        layout.addWidget(mon_group)
        layout.addStretch()

        # Connect radio change
        self.radio_discord.toggled.connect(self._on_routing_mode_changed)
        self.radio_all_mics.toggled.connect(self._on_routing_mode_changed)
        self.radio_custom.toggled.connect(self._on_routing_mode_changed)

        return tab

    def _create_voice_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(14)

        engine_row = QHBoxLayout()
        engine_row.addWidget(QLabel("TTS Engine:"))
        self.engine_combo = QComboBox()
        self.engine_combo.addItem("Microsoft Edge Neural TTS (Ultra-realistic, Online)", "edge-tts")
        self.engine_combo.addItem("Windows SAPI5 Voice (Instant, Fully Offline)", "pyttsx3")
        engine_row.addWidget(self.engine_combo, stretch=1)
        layout.addLayout(engine_row)

        voice_group = QGroupBox("Voice Selection")
        voice_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        v_layout = QVBoxLayout(voice_group)

        v_row = QHBoxLayout()
        self.voice_combo = QComboBox()
        for v in POPULAR_VOICES:
            self.voice_combo.addItem(f"{v['name']}", v["id"])
        v_row.addWidget(self.voice_combo, stretch=1)

        self.preview_voice_btn = QPushButton("Preview Voice")
        self.preview_voice_btn.setProperty("class", "primary")
        self.preview_voice_btn.clicked.connect(self._preview_selected_voice)
        v_row.addWidget(self.preview_voice_btn)
        v_layout.addLayout(v_row)
        layout.addWidget(voice_group)

        # Voice Tuning
        tuning_group = QGroupBox("Voice Tuning")
        tuning_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        t_layout = QVBoxLayout(tuning_group)

        # Rate slider
        rate_row = QHBoxLayout()
        rate_row.addWidget(QLabel("Speaking Speed:"))
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(-50, 50)
        self.rate_slider.setValue(0)
        self.rate_label = QLabel("Normal (+0%)")
        self.rate_slider.valueChanged.connect(self._on_rate_slider_changed)
        rate_row.addWidget(self.rate_slider, stretch=1)
        rate_row.addWidget(self.rate_label)
        t_layout.addLayout(rate_row)

        # Pitch slider
        pitch_row = QHBoxLayout()
        pitch_row.addWidget(QLabel("Voice Pitch:"))
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider.setRange(-50, 50)
        self.pitch_slider.setValue(0)
        self.pitch_label = QLabel("Default (+0Hz)")
        self.pitch_slider.valueChanged.connect(self._on_pitch_slider_changed)
        pitch_row.addWidget(self.pitch_slider, stretch=1)
        pitch_row.addWidget(self.pitch_label)
        t_layout.addLayout(pitch_row)

        layout.addWidget(tuning_group)
        layout.addStretch()
        return tab

    def _create_hotkey_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(16)

        hk_group = QGroupBox("Global Activation Hotkey")
        hk_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        hk_layout = QVBoxLayout(hk_group)

        hk_info = QLabel("Press this key combination anywhere in Windows (even inside games) to type:")
        hk_layout.addWidget(hk_info)

        hk_row = QHBoxLayout()
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("e.g. ctrl+space, alt+t, f8, ctrl+shift+t")
        hk_row.addWidget(self.hotkey_input, stretch=1)

        self.preset_combo = QComboBox()
        self.preset_combo.addItem("Presets...", "")
        self.preset_combo.addItem("Ctrl + Space", "ctrl+space")
        self.preset_combo.addItem("Alt + T", "alt+t")
        self.preset_combo.addItem("F8", "f8")
        self.preset_combo.addItem("Ctrl + Shift + S", "ctrl+shift+s")
        self.preset_combo.currentIndexChanged.connect(self._on_preset_selected)
        hk_row.addWidget(self.preset_combo)

        hk_layout.addLayout(hk_row)
        layout.addWidget(hk_group)

        # Gaming & Focus Group
        beh_group = QGroupBox("Gaming & Focus Behavior")
        beh_group.setStyleSheet("QGroupBox { font-weight: bold; color: #A5B4FC; margin-top: 6px; padding-top: 14px; }")
        beh_layout = QVBoxLayout(beh_group)

        self.auto_hide_cb = QCheckBox("Automatically hide bubble window after pressing Enter to speak")
        beh_layout.addWidget(self.auto_hide_cb)

        gaming_info = QLabel("✓ <b>Smart Gaming Focus</b> is active: When the hotkey is pressed, foreground focus is immediately transferred to the text bubble so game characters won't move or jump. When you hit Enter or Esc, focus returns seamlessly back to your game.")
        gaming_info.setStyleSheet("color: #10B981; font-size: 11px; padding-top: 6px;")
        gaming_info.setWordWrap(True)
        beh_layout.addWidget(gaming_info)

        layout.addWidget(beh_group)
        layout.addStretch()
        return tab

    def _create_phrases_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)

        info = QLabel("Quick canned phrases accessible from the 💬 button in the bubble:")
        layout.addWidget(info)

        self.phrases_list = QListWidget()
        layout.addWidget(self.phrases_list)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("➕ Add Phrase")
        add_btn.setProperty("class", "secondary")
        add_btn.clicked.connect(self._add_phrase)
        btn_row.addWidget(add_btn)

        del_btn = QPushButton("🗑 Remove Selected")
        del_btn.setProperty("class", "secondary")
        del_btn.clicked.connect(self._remove_phrase)
        btn_row.addWidget(del_btn)

        layout.addLayout(btn_row)
        return tab

    def _on_rate_slider_changed(self, val):
        sign = "+" if val >= 0 else ""
        self.rate_label.setText(f"{sign}{val}%")

    def _on_pitch_slider_changed(self, val):
        sign = "+" if val >= 0 else ""
        self.pitch_label.setText(f"{sign}{val}Hz")

    def _on_preset_selected(self, index):
        val = self.preset_combo.currentData()
        if val:
            self.hotkey_input.setText(val)

    def _on_routing_mode_changed(self):
        # Auto-suggest ideal device when switching modes
        if self.radio_discord.isChecked():
            d_auto, _, _ = audio_engine.auto_detect_devices()
            outputs = audio_engine.list_output_devices()
            if d_auto is not None:
                for d in outputs:
                    if d["id"] == d_auto:
                        idx = self.out_combo.findData(d["full_label"])
                        if idx >= 0:
                            self.out_combo.setCurrentIndex(idx)
                        break
        elif self.radio_all_mics.isChecked():
            _, a_auto, _ = audio_engine.auto_detect_devices()
            outputs = audio_engine.list_output_devices()
            if a_auto is not None:
                for d in outputs:
                    if d["id"] == a_auto:
                        idx = self.out_combo.findData(d["full_label"])
                        if idx >= 0:
                            self.out_combo.setCurrentIndex(idx)
                        break

    def _install_dedicated_cable(self):
        import subprocess
        from pathlib import Path
        bat_path = Path(__file__).resolve().parent.parent.parent / "install_cable.bat"
        if bat_path.exists():
            subprocess.Popen(["cmd.exe", "/c", str(bat_path)], shell=True)
            QMessageBox.information(
                self,
                "Installer Launched",
                "The VB-CABLE installer has been launched.\n\n"
                "1. Click 'Yes' on the administrator prompt.\n"
                "2. Click 'Install Driver' in the installer window.\n\n"
                "Once complete, restart Discord and select 'CABLE Output' as your microphone!"
            )
        else:
            QMessageBox.warning(self, "Installer Not Found", "Could not locate install_cable.bat")

    def _populate_audio_devices(self):
        self.out_combo.clear()
        self.mon_combo.clear()

        outputs = audio_engine.list_output_devices()
        self.out_combo.addItem("-- None --", "")
        self.mon_combo.addItem("-- None (No Monitor) --", "")

        for d in outputs:
            label = d["full_label"]
            name_lower = d["name"].lower()
            
            # Unmistakable Discord mapping labels
            if "sonar - microphone" in name_lower:
                display_label = f"⭐ [Discord Dedicated - Active Now!] {label} -> (In Discord: 'SteelSeries Sonar - Microphone')"
            elif "cable input" in name_lower:
                display_label = f"⭐ [Dedicated Discord Cable] {label} -> (In Discord: 'CABLE Output')"
            elif "sonar - chat" in name_lower:
                display_label = f"[Sonar Chat] {label} -> (In Discord: 'Sonar - Chat')"
            elif "voicemeeter input" in name_lower:
                display_label = f"[Voicemeeter VAIO] {label} -> (In Discord: 'Voicemeeter Out B1')"
            elif "voicemeeter vaio3" in name_lower:
                display_label = f"[Voicemeeter VAIO3] {label} -> (In Discord: 'Voicemeeter Out B3')"
            elif "voicemod" in name_lower:
                display_label = f"[Voicemod] {label}"
            else:
                display_label = label

            self.out_combo.addItem(display_label, label)
            self.mon_combo.addItem(label, label)

    def _load_values(self):
        self._populate_audio_devices()

        # Routing Mode
        mode = config.get("routing_mode", "discord_only")
        if mode == "discord_only":
            self.radio_discord.setChecked(True)
        elif mode == "all_mics":
            self.radio_all_mics.setChecked(True)
        else:
            self.radio_custom.setChecked(True)

        # Output device
        saved_dev = config.get("discord_output_device" if mode == "discord_only" else "virtual_mic_device", "")
        if saved_dev:
            idx = self.out_combo.findData(saved_dev)
            if idx >= 0:
                self.out_combo.setCurrentIndex(idx)
        else:
            self._auto_detect_devices()

        # Monitor device
        saved_mon = config.get("monitor_device", "")
        if saved_mon:
            idx = self.mon_combo.findData(saved_mon)
            if idx >= 0:
                self.mon_combo.setCurrentIndex(idx)
        else:
            for i in range(self.mon_combo.count()):
                t = self.mon_combo.itemText(i).lower()
                if "hoofdtelefoon" in t or "arctis" in t or "default" in t or "headphones" in t:
                    self.mon_combo.setCurrentIndex(i)
                    break

        self.mon_enable_cb.setChecked(config.get("play_monitor", True))
        
        vol_mic = int(config.get("volume_mic", 1.0) * 100)
        self.mic_vol_slider.setValue(vol_mic)
        self.mic_vol_label.setText(f"{vol_mic}%")

        vol_mon = int(config.get("volume_monitor", 0.8) * 100)
        self.mon_vol_slider.setValue(vol_mon)
        self.mon_vol_label.setText(f"{vol_mon}%")

        # Engine & Voice
        engine = config.get("tts_engine", "edge-tts")
        e_idx = self.engine_combo.findData(engine)
        if e_idx >= 0:
            self.engine_combo.setCurrentIndex(e_idx)

        voice = config.get("voice", "en-US-ChristopherNeural")
        v_idx = self.voice_combo.findData(voice)
        if v_idx >= 0:
            self.voice_combo.setCurrentIndex(v_idx)

        # Speed & Pitch
        rate_str = config.get("rate", "+0%").replace("%", "").replace("+", "")
        try:
            self.rate_slider.setValue(int(rate_str))
        except Exception:
            self.rate_slider.setValue(0)

        pitch_str = config.get("pitch", "+0Hz").replace("Hz", "").replace("+", "")
        try:
            self.pitch_slider.setValue(int(pitch_str))
        except Exception:
            self.pitch_slider.setValue(0)

        # Hotkey & Phrases
        self.hotkey_input.setText(config.get("hotkey", "ctrl+space"))
        self.auto_hide_cb.setChecked(config.get("auto_hide_on_speak", True))

        self.phrases_list.clear()
        for p in config.get("quick_phrases", []):
            self.phrases_list.addItem(p)

    def _auto_detect_devices(self):
        d_auto, a_auto, m_auto = audio_engine.auto_detect_devices()
        outputs = audio_engine.list_output_devices()

        target_id = d_auto if self.radio_discord.isChecked() else a_auto
        if target_id is not None:
            for d in outputs:
                if d["id"] == target_id:
                    idx = self.out_combo.findData(d["full_label"])
                    if idx >= 0:
                        self.out_combo.setCurrentIndex(idx)
                    break

        if m_auto is not None:
            for d in outputs:
                if d["id"] == m_auto:
                    idx = self.mon_combo.findData(d["full_label"])
                    if idx >= 0:
                        self.mon_combo.setCurrentIndex(idx)
                    break

    def _preview_selected_voice(self):
        voice_id = self.voice_combo.currentData()
        rate_val = self.rate_slider.value()
        pitch_val = self.pitch_slider.value()
        rate = f"{'+' if rate_val >= 0 else ''}{rate_val}%"
        pitch = f"{'+' if pitch_val >= 0 else ''}{pitch_val}Hz"

        test_text = "Hello! This is a preview of my voice."
        old_voice, old_rate, old_pitch = config.get("voice"), config.get("rate"), config.get("pitch")
        config.set("voice", voice_id)
        config.set("rate", rate)
        config.set("pitch", pitch)
        
        audio_engine.speak(test_text)
        
        config.set("voice", old_voice)
        config.set("rate", old_rate)
        config.set("pitch", old_pitch)

    def _test_output(self):
        dest = "Discord" if self.radio_discord.isChecked() else "your microphone"
        audio_engine.speak(f"Testing audio output. Check if {dest} picks up this message.")

    def _test_monitor_output(self):
        audio_engine.speak("Testing headphone monitor playback. You should hear this clearly.")

    def _add_phrase(self):
        text, ok = QInputDialog.getText(self, "Add Quick Phrase", "Enter phrase text:")
        if ok and text.strip():
            self.phrases_list.addItem(text.strip())

    def _remove_phrase(self):
        row = self.phrases_list.currentRow()
        if row >= 0:
            self.phrases_list.takeItem(row)

    def _save_settings(self):
        # Determine routing mode
        if self.radio_discord.isChecked():
            mode = "discord_only"
            config.set("discord_output_device", self.out_combo.currentData() or "")
        elif self.radio_all_mics.isChecked():
            mode = "all_mics"
            config.set("virtual_mic_device", self.out_combo.currentData() or "")
        else:
            mode = "custom"
            config.set("virtual_mic_device", self.out_combo.currentData() or "")

        config.set("routing_mode", mode)
        config.set("monitor_device", self.mon_combo.currentData() or "")
        config.set("play_monitor", self.mon_enable_cb.isChecked())
        config.set("volume_mic", self.mic_vol_slider.value() / 100.0)
        config.set("volume_monitor", self.mon_vol_slider.value() / 100.0)

        # Voice
        config.set("tts_engine", self.engine_combo.currentData())
        config.set("voice", self.voice_combo.currentData())
        
        r_val = self.rate_slider.value()
        config.set("rate", f"{'+' if r_val >= 0 else ''}{r_val}%")
        p_val = self.pitch_slider.value()
        config.set("pitch", f"{'+' if p_val >= 0 else ''}{p_val}Hz")

        # Hotkey & General
        new_hotkey = self.hotkey_input.text().strip().lower()
        old_hotkey = config.get("hotkey", "ctrl+space")
        config.set("hotkey", new_hotkey)
        config.set("auto_hide_on_speak", self.auto_hide_cb.isChecked())

        phrases = [self.phrases_list.item(i).text() for i in range(self.phrases_list.count())]
        config.set("quick_phrases", phrases)

        config.save()

        if new_hotkey != old_hotkey:
            self.hotkeyChanged.emit(new_hotkey)

        self.accept()
