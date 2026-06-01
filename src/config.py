import json
import os

CONFIG_DIR  = os.path.expanduser('~/.config/ma-sidebar')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

DEFAULT_CONFIG = {
    'url':        None,
    'panel_side': 'right',
}


def load():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def has_url():
    return bool(load().get('url'))
