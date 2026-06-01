import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AyatanaAppIndicator3', '0.1')
from gi.repository import Gtk, AyatanaAppIndicator3 as AppIndicator3

ICON_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'ma-icon.svg')


class GtkTray:
    def __init__(self, command_queue):
        self.queue = command_queue

    def start(self):
        icon = ICON_PATH if os.path.exists(ICON_PATH) else 'audio-x-generic'

        indicator = AppIndicator3.Indicator.new(
            'ma-sidebar',
            icon,
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        indicator.set_menu(self._build_menu())

        Gtk.main()

    def _build_menu(self):
        menu = Gtk.Menu()

        toggle = Gtk.MenuItem(label='Toggle Sidebar')
        toggle.connect('activate', lambda _: self.queue.put('toggle'))
        menu.append(toggle)

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label='Quit')
        quit_item.connect('activate', lambda _: self.queue.put('quit'))
        menu.append(quit_item)

        menu.show_all()
        return menu
