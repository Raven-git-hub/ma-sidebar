import subprocess

# GNOME accent colour name -> hex
GNOME_ACCENT_MAP = {
    'blue':   '#3584e4',
    'teal':   '#2190a4',
    'green':  '#3a944a',
    'yellow': '#c88800',
    'orange': '#e66100',
    'red':    '#e01b24',
    'pink':   '#d56199',
    'purple': '#9141ac',
    'slate':  '#6f8396',
}

# Default accent if system colour can't be read
DEFAULT_ACCENT = '#9141ac'  # purple — fits a music player well


def get_accent_colour():
    """
    Read the system accent colour from GNOME settings.
    Falls back to DEFAULT_ACCENT if unavailable (e.g. Pop!_OS, older GNOME).
    """
    try:
        result = subprocess.run(
            ['gsettings', 'get', 'org.gnome.desktop.interface', 'accent-color'],
            capture_output=True, text=True, timeout=2
        )
        colour = result.stdout.strip().strip("'")
        return GNOME_ACCENT_MAP.get(colour, DEFAULT_ACCENT)
    except Exception:
        return DEFAULT_ACCENT


def accent_dim(hex_colour, alpha=0.15):
    """Return a rgba() string with low opacity for backgrounds."""
    r = int(hex_colour[1:3], 16)
    g = int(hex_colour[3:5], 16)
    b = int(hex_colour[5:7], 16)
    return f'rgba({r},{g},{b},{alpha})'
