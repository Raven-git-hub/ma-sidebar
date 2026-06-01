import urllib.request
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton
)
from PyQt5.QtCore import Qt
from theme import get_accent_colour, accent_dim


def build_style(accent):
    return f"""
    QDialog, QWidget {{
        background-color: #0d0d18;
        color: #e2e2f0;
    }}
    QLabel {{
        color: #e2e2f0;
        font-size: 12px;
    }}
    QLabel#title {{
        font-size: 15px;
        font-weight: bold;
        color: {accent};
    }}
    QLabel#subtitle {{
        font-size: 11px;
        color: #7b7b99;
    }}
    QLineEdit {{
        background: rgba(255,255,255,0.05);
        border: 1px solid #2a2a3d;
        border-radius: 6px;
        padding: 0px 10px;
        min-height: 36px;
        color: #e2e2f0;
        font-size: 12px;
    }}
    QLineEdit:focus {{
        border-color: {accent};
    }}
    QPushButton {{
        background: rgba(255,255,255,0.05);
        border: 1px solid #2a2a3d;
        border-radius: 6px;
        padding: 8px 16px;
        color: #e2e2f0;
        font-size: 12px;
    }}
    QPushButton:hover {{
        background: rgba(255,255,255,0.09);
        border-color: #3a3a55;
    }}
    QPushButton#save_btn {{
        background: {accent_dim(accent)};
        border-color: {accent};
        color: {accent};
        font-weight: bold;
    }}
    QPushButton#save_btn:hover {{
        background: {accent_dim(accent, 0.25)};
    }}
"""


class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.accent      = get_accent_colour()
        self.result_url  = None
        self._build()

    def _build(self):
        self.setWindowTitle('MA Sidebar Setup')
        self.setFixedSize(440, 280)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet(build_style(self.accent))

        layout = QVBoxLayout()
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel('Welcome to MA Sidebar')
        title.setObjectName('title')
        layout.addWidget(title)

        subtitle = QLabel('Enter the URL of your Music Assistant instance.')
        subtitle.setObjectName('subtitle')
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        layout.addWidget(QLabel('Music Assistant URL'))
        self.url_input = QLineEdit()
        self.url_input.setFixedHeight(36)
        self.url_input.setPlaceholderText('http://192.168.x.x:8123/your_music_assistant')
        layout.addWidget(self.url_input)

        self.status_lbl = QLabel('')
        self.status_lbl.setFixedHeight(18)
        layout.addWidget(self.status_lbl)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        test_btn = QPushButton('Test Connection')
        test_btn.clicked.connect(self._test_connection)
        btn_row.addWidget(test_btn)

        btn_row.addStretch()

        save_btn = QPushButton('Save')
        save_btn.setObjectName('save_btn')
        save_btn.clicked.connect(self._save)
        btn_row.addWidget(save_btn)

        layout.addLayout(btn_row)
        self.setLayout(layout)

    def _test_connection(self):
        url = self.url_input.text().strip()
        if not url:
            self._set_status('Enter a URL first', error=True)
            return
        self._set_status('Testing…', color='#7b7b99')
        self.repaint()
        try:
            urllib.request.urlopen(url, timeout=5)
            self._set_status('✓  Connected successfully', color='#22c55e')
        except Exception:
            self._set_status('✗  Could not connect — check the URL and network', error=True)

    def _save(self):
        url = self.url_input.text().strip()
        if not url:
            self._set_status('Enter the Music Assistant URL', error=True)
            return
        self.result_url = url
        self.accept()

    def _set_status(self, msg, error=False, color=None):
        c = color or ('#ef4444' if error else '#e2e2f0')
        self.status_lbl.setStyleSheet(f'color: {c}; font-size: 11px;')
        self.status_lbl.setText(msg)

    def get_result(self):
        return self.result_url
