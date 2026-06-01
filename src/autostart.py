import os
import sys

AUTOSTART_DIR  = os.path.expanduser('~/.config/autostart')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'ma-sidebar.desktop')


def is_enabled():
    return os.path.exists(AUTOSTART_FILE)


def enable():
    os.makedirs(AUTOSTART_DIR, exist_ok=True)
    main_py = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'main.py')
    )
    python = sys.executable

    desktop = f"""[Desktop Entry]
Type=Application
Name=MA Sidebar
Comment=Music Assistant sidebar panel
Exec=bash -c "sleep 5 && {python} {main_py}"
Icon=audio-x-generic
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
    with open(AUTOSTART_FILE, 'w') as f:
        f.write(desktop)


def disable():
    if os.path.exists(AUTOSTART_FILE):
        os.remove(AUTOSTART_FILE)
