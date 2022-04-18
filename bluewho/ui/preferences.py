##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2009-2022 Fabio Castelli
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

from gi.repository import Gtk

from bluewho.constants import FILE_ICON
from bluewho.functions import _
from bluewho.settings import Preferences
from bluewho.ui.base import UIBase


class DialogPreferences(UIBase):
    def __init__(self, settings, parent, show=False):
        super().__init__(filename='preferences.glade')
        self.settings = settings
        # Obtain widget references
        dialog = self.ui.dialog
        # Set various properties
        dialog.set_title(_('Preferences'))
        dialog.set_icon_from_file(FILE_ICON)
        dialog.set_transient_for(parent)
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        self.ui.chkStartupScan.set_active(
            settings.get_value(Preferences.STARTUPSCAN))
        self.ui.chkRestoreSize.set_active(
            settings.get_value(Preferences.RESTORE_SIZE))
        self.ui.adjScanSpeed.set_value(
            settings.get_value(Preferences.SCAN_SPEED))
        self.ui.chkRetrieveName.set_active(
            settings.get_value(Preferences.RETRIEVE_NAMES))
        self.ui.chkResolveNames.set_active(
            settings.get_value(Preferences.RESOLVE_NAMES))
        self.ui.chkLocalAdapters.set_active(
            settings.get_value(Preferences.SHOW_LOCAL))
        self.ui.chkNotification.set_active(
            settings.get_value(Preferences.NOTIFICATION))
        self.ui.chkPlaySound.set_active(
            settings.get_value(Preferences.PLAY_SOUND))
        # Optionally show the dialog
        if show:
            self.show()

    def show(self):
        """Show the Preferences dialog"""
        self.ui.dialog.run()
        self.ui.dialog.hide()
        # Save the values back in the configuration
        self.settings.set_value(Preferences.STARTUPSCAN,
                                self.ui.chkStartupScan.get_active())
        self.settings.set_value(Preferences.RESTORE_SIZE,
                                self.ui.chkRestoreSize.get_active())
        self.settings.set_value(Preferences.SCAN_SPEED,
                                int(self.ui.adjScanSpeed.get_value()))
        self.settings.set_value(Preferences.RETRIEVE_NAMES,
                                self.ui.chkRetrieveName.get_active())
        self.settings.set_value(Preferences.RESOLVE_NAMES,
                                self.ui.chkResolveNames.get_active())
        self.settings.set_value(Preferences.SHOW_LOCAL,
                                self.ui.chkLocalAdapters.get_active())
        self.settings.set_value(Preferences.NOTIFICATION,
                                self.ui.chkNotification.get_active())
        self.settings.set_value(Preferences.PLAY_SOUND,
                                self.ui.chkPlaySound.get_active())

    def destroy(self):
        """Destroy the Preferences dialog"""
        self.ui.dialog.destroy()
