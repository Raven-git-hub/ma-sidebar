from urllib.parse import urlparse

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QDialog
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PyQt6.QtCore import Qt, QUrl, QTimer

import config as cfg
from theme import get_accent_colour, accent_dim

PANEL_WIDTH = 840

# JavaScript nav lock — intercepts MA's SPA routing and redirects
# back to the configured URL if the user navigates elsewhere
NAV_LOCK_JS = """
(function() {{
    const allowed = '{path}';
    const check = () => {{
        const path = window.location.pathname;
        if (!path.startsWith(allowed) && !path.startsWith('/auth')) {{
            window.location.replace(allowed);
        }}
    }};
    const orig = history.pushState.bind(history);
    history.pushState = function(...args) {{
        orig(...args);
        setTimeout(check, 50);
    }};
    window.addEventListener('popstate', check);
}})();
"""

# Traverses shadow DOM to hide MA's sidebar toggle button
HIDE_SIDEBAR_BTN_JS = """
(function() {
    function hideButton() {
        function walk(root) {
            const el = root.querySelector('ha-icon-button[aria-label="Sidebar toggle"]');
            if (el) {
                el.style.setProperty('display', 'none', 'important');
                return true;
            }
            for (const child of root.querySelectorAll('*')) {
                if (child.shadowRoot && walk(child.shadowRoot)) return true;
            }
            return false;
        }
        walk(document);
    }
    hideButton();
    const observer = new MutationObserver(hideButton);
    observer.observe(document.body, { childList: true, subtree: true });
    setTimeout(() => observer.disconnect(), 10000);
})();
"""


def build_style(accent):
    return f"""
    QWidget {{
        background-color: #0d0d18;
        color: #e2e2f0;
    }}
    QLabel {{
        color: #e2e2f0;
        font-size: 13px;
    }}
    QPushButton {{
        color: #7b7b99;
        background: transparent;
        border: 1px solid #2a2a3d;
        border-radius: 5px;
        font-size: 13px;
        padding: 2px 6px;
    }}
    QPushButton:hover {{
        color: #e2e2f0;
        background: rgba(255,255,255,0.06);
        border-color: #3a3a55;
    }}
"""


class LockedWebPage(QWebEnginePage):
    """Blocks main-frame navigation outside the configured MA URL."""
    def __init__(self, instance_url, profile, parent=None):
        super().__init__(profile, parent)
        parsed = urlparse(instance_url)
        self.allowed_origin = f"{parsed.scheme}://{parsed.netloc}"

    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        if not is_main_frame:
            return True
        if url.toString().startswith(self.allowed_origin):
            return True
        print(f"[nav lock] Blocked: {url.toString()}")
        return False


class LoadingPage(QWidget):
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def __init__(self, accent, parent=None):
        super().__init__(parent)
        self._frame  = 0
        self._timer  = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._accent = accent
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        self.spinner = QLabel(self.FRAMES[0])
        self.spinner.setStyleSheet(f'color: {self._accent}; font-size: 32px;')
        self.spinner.setAlignment(Qt.AlignmentFlag.AlignCenter)

        msg = QLabel('Connecting to Music Assistant…')
        msg.setStyleSheet('color: #7b7b99; font-size: 12px;')
        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.spinner)
        layout.addWidget(msg)
        self.setLayout(layout)
        self.setStyleSheet('background-color: #0d0d18;')

    def showEvent(self, event):
        self._timer.start(80)
        super().showEvent(event)

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def _tick(self):
        self._frame = (self._frame + 1) % len(self.FRAMES)
        self.spinner.setText(self.FRAMES[self._frame])


class SidebarPanel(QWidget):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen
        self.config = cfg.load()
        self.accent = get_accent_colour()
        self.url    = self.config.get('url', '')
        self._build()

    def _build(self):
        geo = self.screen.geometry()

        self.setWindowFlags(
            Qt.WindowType.Tool                |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setGeometry(
            geo.width() - PANEL_WIDTH, 0,
            PANEL_WIDTH, geo.height()
        )
        self.setWindowOpacity(0.93)
        self.setStyleSheet(build_style(self.accent))

        # ── header ──────────────────────────────────────────
        header = QHBoxLayout()
        header.setContentsMargins(12, 8, 8, 8)
        header.setSpacing(8)

        icon_lbl = QLabel('♫')
        icon_lbl.setStyleSheet(f'color: {self.accent}; font-size: 18px; padding-right: 2px;')
        icon_lbl.setFixedWidth(24)
        header.addWidget(icon_lbl)

        title_lbl = QLabel('Music Assistant')
        title_lbl.setStyleSheet('color: #e2e2f0; font-size: 12px; font-weight: bold;')
        header.addWidget(title_lbl, 1)

        close_btn = QPushButton('✕')
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.hide)
        header.addWidget(close_btn)

        header_widget = QWidget()
        header_widget.setLayout(header)
        header_widget.setFixedHeight(48)

        separator = QWidget()
        separator.setFixedHeight(1)
        separator.setStyleSheet('background-color: #2a2a3d;')

        # ── webview stack ────────────────────────────────────
        self.stack = QStackedWidget()

        self.loading = LoadingPage(self.accent)
        self.stack.addWidget(self.loading)

        profile      = QWebEngineProfile('ma-sidebar', self)
        page         = LockedWebPage(self.url, profile, self)
        self.webview = QWebEngineView()
        self.webview.setPage(page)
        self.stack.addWidget(self.webview)

        self.stack.setCurrentIndex(0)

        self.webview.loadFinished.connect(self._on_load_finished)
        self.webview.load(QUrl(self.url))

        # ── layout ───────────────────────────────────────────
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(header_widget)
        layout.addWidget(separator)
        layout.addWidget(self.stack)
        self.setLayout(layout)

    def _on_load_finished(self, ok):
        if ok:
            self.stack.setCurrentIndex(1)
            # Inject JS nav lock
            parsed = urlparse(self.url)
            js     = NAV_LOCK_JS.format(path=parsed.path)
            self.webview.page().runJavaScript(js)
            # Hide sidebar toggle button
            self.webview.page().runJavaScript(HIDE_SIDEBAR_BTN_JS)
            # Disable horizontal scroll
            self.webview.page().runJavaScript(
                "document.documentElement.style.overflowX = 'hidden';"
            )

    def showEvent(self, event):
        geo = self.screen.geometry()
        self.setGeometry(
            geo.width() - PANEL_WIDTH, 0,
            PANEL_WIDTH, geo.height()
        )
        super().showEvent(event)

    def hideEvent(self, event):
        for child in self.findChildren(QDialog):
            child.close()
        super().hideEvent(event)

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
