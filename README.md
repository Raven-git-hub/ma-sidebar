# MA Sidebar

A Linux desktop sidebar for [Music Assistant](https://music-assistant.io/). Sits in your system tray and slides out a dedicated music player panel — one click access to your music from your desktop.

> **Built for locally hosted Music Assistant instances on the same network.**

---

## Features

- **System tray icon** — click to toggle the panel open and closed
- **Embedded Music Assistant UI** — loads MA directly in the sidebar, full functionality with no browser needed
- **Navigation lock** — keeps the panel within Music Assistant, blocks external links
- **Clean interface** — MA's navigation chrome is hidden, leaving only the music player UI
- **System accent colour** — the panel chrome follows your GNOME accent colour setting
- **First-run setup** — guided setup on first launch with connection test
- **Autostart** — optional launch on login, set up during first run

---

## Requirements

- Linux with GNOME desktop (tested on **Pop!_OS** and **Ubuntu**)
- Python 3.10+
- The [AppIndicator and KStatusNotifierItem Support](https://extensions.gnome.org/extension/615/appindicator-support/) GNOME extension enabled
- A running Music Assistant instance accessible on your local network

---

## Installation

### 1. Clone the repo

```bash
git clone https://github.com/Raven-git-hub/ma-sidebar.git
cd ma-sidebar
```

### 2. Install dependencies

```bash
sudo apt install \
  python3-gi \
  python3-gi-cairo \
  gir1.2-ayatanaappindicator3-0.1 \
  libxcb-cursor0

pip3 install PyQt6 PyQt6-WebEngine --user
```

### 3. Run

```bash
python3 src/main.py
```

On first launch you'll be prompted for your Music Assistant URL. After that, the app lives in your system tray.

---

## Music Assistant Setup

MA Sidebar loads your Music Assistant instance directly. You'll need the full URL including the path.

1. Open Music Assistant in your browser
2. Copy the full URL (e.g. `http://192.168.1.x:8123/d5369777_music_assistant`)
3. Paste that URL into MA Sidebar during setup

MA Sidebar works with both standalone Music Assistant instances and those running as a Home Assistant addon via ingress.

---

## Usage

| Action | Result |
|---|---|
| **Click tray icon** | Opens setup on first run, toggles panel afterwards |
| **Right-click tray icon** | Shows menu (Toggle Sidebar, Quit) |
| **Escape** | Closes the panel |
| **Close button (✕)** | Closes the panel |

---

## Known Limitations

- **Wayland** — panel transparency is not supported on Wayland sessions. Positioning works via XWayland. Full native Wayland support is planned.
- **Tray left-click** — due to a limitation in AppIndicator3 on GNOME, left and right click both open the menu. Toggle Sidebar is the first item in the menu. A keyboard shortcut can be set in GNOME Settings as an alternative.

---

## Autostart

During first-run setup you'll be asked if you want MA Sidebar to launch on login. The autostart entry is installed to `~/.config/autostart/ma-sidebar.desktop`.

---

## Contributing

Issues and pull requests are welcome. If you're reporting a bug, please include:

- Your distro and version
- GNOME Shell version (`gnome-shell --version`)
- Session type (`echo $XDG_SESSION_TYPE`)
- Any terminal output from running `python3 src/main.py`

---

## License

MIT
