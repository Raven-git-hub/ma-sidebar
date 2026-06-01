#!/usr/bin/env python3
import sys
import os
import signal
import queue
import threading

# Force XCB so positioning works on both X11 and XWayland
os.environ.setdefault('QT_QPA_PLATFORM', 'xcb')

sys.path.insert(0, os.path.dirname(__file__))

from PyQt6.QtWidgets import QApplication, QDialog, QMessageBox
from PyQt6.QtCore import QTimer

import config as cfg
import autostart
from setup_dialog import SetupDialog
from panel import SidebarPanel
from tray_gtk import GtkTray


def prompt_autostart():
    msg = QMessageBox()
    msg.setWindowTitle('Launch on startup?')
    msg.setText('Would you like MA Sidebar to launch automatically when you log in?')
    msg.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg.setDefaultButton(QMessageBox.StandardButton.Yes)
    msg.setStyleSheet("""
        QMessageBox { background-color: #0d0d18; color: #e2e2f0; }
        QLabel { color: #e2e2f0; font-size: 13px; }
        QPushButton {
            background: rgba(255,255,255,0.05);
            border: 1px solid #2a2a3d;
            border-radius: 6px;
            padding: 6px 16px;
            color: #e2e2f0;
            min-width: 60px;
        }
        QPushButton:hover { background: rgba(255,255,255,0.09); border-color: #3a3a55; }
    """)
    if msg.exec() == QMessageBox.StandardButton.Yes:
        autostart.enable()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # ── first run ────────────────────────────────────────────
    if not cfg.has_url():
        dialog = SetupDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            config        = cfg.load()
            config['url'] = dialog.get_result()
            cfg.save(config)
            prompt_autostart()
        else:
            sys.exit(0)

    # ── start app ────────────────────────────────────────────
    screen = app.primaryScreen()
    panel  = SidebarPanel(screen)

    cmd_queue   = queue.Queue()
    gtk_tray    = GtkTray(cmd_queue)
    tray_thread = threading.Thread(target=gtk_tray.start, daemon=True)
    tray_thread.start()

    def process_commands():
        try:
            cmd = cmd_queue.get_nowait()
            if cmd == 'toggle':
                panel.toggle()
            elif cmd == 'quit':
                app.quit()
        except queue.Empty:
            pass

    timer = QTimer()
    timer.timeout.connect(process_commands)
    timer.start(100)

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
