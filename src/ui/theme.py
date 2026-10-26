"""Modern Dark Glassmorphic Design System for QuickTTS"""

COLORS = {
    "bg_main": "#0E1017",
    "bg_surface": "#161926",
    "bg_card": "#1E2235",
    "bg_hover": "#262C44",
    "border_subtle": "#282E47",
    "border_focus": "#6366F1",
    "border_glow": "rgba(99, 102, 241, 0.5)",
    "accent_primary": "#6366F1",     # Indigo
    "accent_secondary": "#8B5CF6",   # Purple
    "accent_cyan": "#06B6D4",        # Cyan
    "accent_green": "#10B981",       # Emerald
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "danger": "#EF4444",
}

BUBBLE_STYLE = """
QFrame#BubbleContainer {
    background-color: rgba(14, 16, 23, 0.95);
    border: 1.5px solid #313854;
    border-radius: 20px;
}
QFrame#BubbleContainer:hover {
    border: 1.5px solid #6366F1;
}

QLineEdit#TextInput {
    background: transparent;
    border: none;
    color: #F8FAFC;
    font-size: 15px;
    font-family: 'Segoe UI', system-ui, sans-serif;
    padding: 0px 4px;
    selection-background-color: #6366F1;
}
QLineEdit#TextInput:placeholder {
    color: #64748B;
    font-style: italic;
}

QPushButton#VoiceChip {
    background-color: #1E2235;
    border: 1px solid #2F3754;
    border-radius: 12px;
    color: #A5B4FC;
    font-size: 11px;
    font-weight: bold;
    padding: 4px 10px;
}
QPushButton#VoiceChip:hover {
    background-color: #2E3654;
    border-color: #6366F1;
    color: #FFFFFF;
}

QPushButton#IconButton {
    background: transparent;
    border: none;
    border-radius: 12px;
    color: #94A3B8;
    padding: 4px;
}
QPushButton#IconButton:hover {
    background-color: #1E2235;
    color: #F8FAFC;
}

QLabel#MicIcon {
    color: #6366F1;
    font-size: 18px;
    font-weight: bold;
}
"""

SETTINGS_STYLE = """
QDialog {
    background-color: #0E1017;
    color: #F8FAFC;
    font-family: 'Segoe UI', system-ui, sans-serif;
}

QLabel {
    color: #F8FAFC;
    font-size: 13px;
}

QLabel.title {
    font-size: 18px;
    font-weight: bold;
    color: #FFFFFF;
}

QLabel.subtitle {
    font-size: 12px;
    color: #94A3B8;
}

QTabWidget::pane {
    border: 1px solid #252A40;
    border-radius: 12px;
    background-color: #141724;
    padding: 12px;
}

QTabBar::tab {
    background: #0E1017;
    color: #94A3B8;
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid #252A40;
    border-bottom: none;
    font-weight: 500;
}

QTabBar::tab:selected {
    background: #141724;
    color: #FFFFFF;
    border-top: 2px solid #6366F1;
}

QTabBar::tab:hover:!selected {
    background: #1B2032;
    color: #E2E8F0;
}

QComboBox {
    background-color: #1A1F30;
    border: 1px solid #2E3550;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 7px 12px;
    font-size: 13px;
}
QComboBox:hover {
    border-color: #4F46E5;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #161926;
    border: 1px solid #2E3550;
    color: #F8FAFC;
    selection-background-color: #4F46E5;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #252A40;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #6366F1;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #FFFFFF;
    border: 2px solid #6366F1;
    width: 16px;
    height: 16px;
    margin: -5px 0;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #A5B4FC;
    border-color: #4F46E5;
}

QPushButton.primary {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6);
    color: #FFFFFF;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    font-size: 13px;
}
QPushButton.primary:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:1 #7C3AED);
}

QPushButton.secondary {
    background-color: #1E2235;
    color: #E2E8F0;
    border: 1px solid #2F3754;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 13px;
}
QPushButton.secondary:hover {
    background-color: #2E3654;
    border-color: #4F46E5;
    color: #FFFFFF;
}

QCheckBox {
    color: #F8FAFC;
    font-size: 13px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid #333C5C;
    background: #1A1F30;
}
QCheckBox::indicator:checked {
    background: #6366F1;
    border-color: #6366F1;
}

QLineEdit {
    background-color: #1A1F30;
    border: 1px solid #2E3550;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 7px 12px;
    font-size: 13px;
}
QLineEdit:focus {
    border-color: #6366F1;
}

QListWidget {
    background-color: #1A1F30;
    border: 1px solid #2E3550;
    border-radius: 8px;
    color: #F8FAFC;
    padding: 6px;
}
QListWidget::item {
    padding: 6px 10px;
    border-radius: 6px;
}
QListWidget::item:hover {
    background-color: #252B42;
}
QListWidget::item:selected {
    background-color: #4F46E5;
    color: #FFFFFF;
}
"""
