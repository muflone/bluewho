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

from gi.repository import Gtk

from bluewho.constants import (FILE_ICON,
                               FILE_UI_PREFERENCES)
from bluewho.functions import _
from bluewho.settings import Preferences


class DialogPreferences(object):
    def __init__(self, settings, winParent, show=False):
        self.settings = settings
        # Load the user interface
        builder = Gtk.Builder()
        builder.add_from_file(FILE_UI_PREFERENCES)
        # Obtain widget references
        self.dialog = builder.get_object('dialogPreferences')
        self.chkStartupScan = builder.get_object('chkStartupScan')
        self.chkRestoreSize = builder.get_object('chkRestoreSize')
        self.adjScanSpeed = builder.get_object('adjScanSpeed')
        self.chkRetrieveName = builder.get_object('chkRetrieveName')
        self.chkResolveNames = builder.get_object('chkResolveNames')
        self.chkLocalAdapters = builder.get_object('chkLocalAdapters')
        self.chkNotification = builder.get_object('chkNotification')
        self.chkPlaySound = builder.get_object('chkPlaySound')
        # Set various properties
        self.dialog.set_title(_('Preferences'))
        self.dialog.set_icon_from_file(FILE_ICON)
        self.dialog.set_transient_for(winParent)
        self.dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        self.dialog.set_default_response(Gtk.ResponseType.OK)
        self.chkStartupScan.set_active(
            settings.get_value(Preferences.STARTUPSCAN))
        self.chkRestoreSize.set_active(
            settings.get_value(Preferences.RESTORE_SIZE))
        self.adjScanSpeed.set_value(
            settings.get_value(Preferences.SCAN_SPEED))
        self.chkRetrieveName.set_active(
            settings.get_value(Preferences.RETRIEVE_NAMES))
        self.chkResolveNames.set_active(
            settings.get_value(Preferences.RESOLVE_NAMES))
        self.chkLocalAdapters.set_active(
            settings.get_value(Preferences.SHOW_LOCAL))
        self.chkNotification.set_active(
            settings.get_value(Preferences.NOTIFICATION))
        self.chkPlaySound.set_active(
            settings.get_value(Preferences.PLAY_SOUND))
        # Optionally show the dialog
        if show:
            self.show()

    def show(self):
        """Show the Preferences dialog"""
        self.dialog.run()
        self.dialog.hide()
        # Save the values back in the configuration
        self.settings.set_value(Preferences.STARTUPSCAN,
                                self.chkStartupScan.get_active())
        self.settings.set_value(Preferences.RESTORE_SIZE,
                                self.chkRestoreSize.get_active())
        self.settings.set_value(Preferences.SCAN_SPEED,
                                int(self.adjScanSpeed.get_value()))
        self.settings.set_value(Preferences.RETRIEVE_NAMES,
                                self.chkRetrieveName.get_active())
        self.settings.set_value(Preferences.RESOLVE_NAMES,
                                self.chkResolveNames.get_active())
        self.settings.set_value(Preferences.SHOW_LOCAL,
                                self.chkLocalAdapters.get_active())
        self.settings.set_value(Preferences.NOTIFICATION,
                                self.chkNotification.get_active())
        self.settings.set_value(Preferences.PLAY_SOUND,
                                self.chkPlaySound.get_active())

    def destroy(self):
        """Destroy the Preferences dialog"""
        self.dialog.destroy()
        self.dialog = None