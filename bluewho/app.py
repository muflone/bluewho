##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2009-2021 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

from gi.repository import Gtk, Gio

from bluewho.constants import APP_ID, FILE_UI_APPMENU
from bluewho.ui.main import MainWindow


class Application(Gtk.Application):
    def __init__(self, settings, btsupport):
        super(self.__class__, self).__init__(application_id=APP_ID)
        self.settings = settings
        self.btsupport = btsupport
        self.connect('activate', self.activate)
        self.connect('startup', self.startup)

    def startup(self, application):
        """Configure the application during the startup"""
        self.ui = MainWindow(self, self.settings, self.btsupport)
        # Add the actions related to the app menu
        action = Gio.SimpleAction(name='about')
        action.connect('activate', self.on_app_about_activate)
        self.add_action(action)

        action = Gio.SimpleAction(name='preferences')
        action.connect('activate', self.on_app_preferences_activate)
        self.add_action(action)

        action = Gio.SimpleAction(name='scan')
        action.connect('activate', self.on_app_scan_activate)
        self.add_action(action)

        action = Gio.SimpleAction(name='clear')
        action.connect('activate', self.on_app_clear_activate)
        self.add_action(action)

        action = Gio.SimpleAction(name='quit')
        action.connect('activate', self.on_app_quit_activate)
        self.add_action(action)
        # Add the app menu
        builder = Gtk.Builder()
        builder.add_from_file(FILE_UI_APPMENU)
        menubar = builder.get_object('app-menu')
        self.set_app_menu(menubar)

    def activate(self, application):
        """Execute the application"""
        self.ui.run()

    def on_app_about_activate(self, action, data):
        """Show the about dialog from the app menu"""
        self.ui.on_toolbAbout_clicked(self)

    def on_app_scan_activate(self, action, data):
        """Toggle the scan button"""
        if self.ui.toolbDetect.get_sensitive():
            self.ui.toolbDetect.set_active(
                not self.ui.toolbDetect.get_active())

    def on_app_clear_activate(self, action, data):
        """Clear the results list"""
        self.ui.on_toolbClear_clicked(self)

    def on_app_preferences_activate(self, action, data):
        """Show the preferences dialog from the app menu"""
        self.ui.on_toolbPreferences_clicked(self)

    def on_app_quit_activate(self, action, data):
        """Quit the application from the app menu"""
        self.ui.on_winMain_delete_event(self, None)
