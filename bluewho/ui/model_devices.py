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

import os.path

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import Notify

from bluewho.audio_player import AudioPlayer
from bluewho.constants import (APP_NAME,
                               DIR_BT_ICONS,
                               FILE_SOUND,
                               VERBOSE_LEVEL_MAX)
from bluewho.functions import _
from bluewho.settings import Preferences


class ModelDevices(object):
    COL_ICON = 0
    COL_ICON_NAME = 1
    COL_CLASS = 2
    COL_TYPE = 3
    COL_TYPE_TRANSLATED = 4
    COL_SUBTYPE = 5
    COL_SUBTYPE_TRANSLATED = 6
    COL_NAME = 7
    COL_ADDRESS = 8
    COL_LASTSEEN = 9

    def __init__(self, model, settings, btsupport):
        self.model = model
        self.settings = settings
        self.btsupport = btsupport
        self.devices = {}
        self.audio_player = AudioPlayer()
        Notify.init(APP_NAME)

    def destroy(self):
        """Destroy any pending objects"""
        self.clear()
        self.model = None
        self.settings = None
        self.btsupport = None
        self.devices = None
        self.audio_player = None

    def clear(self):
        """Clear the devices list"""
        self.devices = {}
        return self.model.clear()

    def add_device(self, address, name, device_class, last_seen, notify):
        """Add a new device to the list and pops notification"""
        minor_class, major_class, services_class = self.btsupport.get_classes(
            device_class)
        device_type = self.btsupport.get_device_type(major_class)
        icon_filename, device_subtype = self.btsupport.get_device_detail(
            major_class, minor_class)
        if device_subtype == 'adapter':
            device_type = 'adapter'
        icon_path = os.path.join(DIR_BT_ICONS, icon_filename)
        if not os.path.isfile(icon_path):
            icon_filename = 'unknown.png'
            icon_path = os.path.join(DIR_BT_ICONS, icon_filename)
        # Replace None with empty string in name
        if name is None:
            name = ''
        if address in self.devices:
            # Update the existing device in the model
            treeiter = self.devices[address]
            # Resolve the undetected name if Preferences.RESOLVE_NAMES is set
            if self.settings.get_value(Preferences.RESOLVE_NAMES) and not name:
                name = self.btsupport.get_device_name(address)
                self.settings.logText('Resolved device %s name to "%s"' % (
                    address, name), VERBOSE_LEVEL_MAX)
            # Update icon
            old_value = self.get_icon(treeiter)
            if icon_path != old_value:
                self.settings.logText(
                    'Updated device "%s" icon from %s to %s' % (
                        name,
                        os.path.basename(old_value),
                        os.path.basename(icon_path)),
                    VERBOSE_LEVEL_MAX)
                self.set_icon(treeiter, icon_path)
            # Update device name
            old_value = self.get_name(treeiter)
            if name and name != old_value:
                self.settings.logText('Updated device "%s" name from '
                                      '"%s" to "%s"' % (name,
                                                        old_value,
                                                        name),
                                      VERBOSE_LEVEL_MAX)
                self.set_name(treeiter, name)
            # Update device class
            old_value = self.get_class(treeiter)
            if device_class != old_value:
                self.settings.logText('Updated device "%s" class from '
                                      '%d to %d' % (name,
                                                    old_value,
                                                    device_class),
                                      VERBOSE_LEVEL_MAX)
                self.set_class(treeiter, device_class)
            # Update device type
            old_value = self.get_type(treeiter)
            if device_type != old_value:
                self.settings.logText('Updated device "%s" type from '
                                      '%s to %s' % (name,
                                                    old_value,
                                                    device_type),
                                      VERBOSE_LEVEL_MAX)
                self.set_type(treeiter, device_type)
            # Update device subtype
            old_value = self.get_subtype(treeiter)
            if device_subtype != old_value:
                self.settings.logText('Updated device "%s" subtype from '
                                      '%s to %s' % (name,
                                                    old_value,
                                                    device_subtype),
                                      VERBOSE_LEVEL_MAX)
                self.set_subtype(treeiter, device_subtype)
            # Update device last seen time (always)
            self.set_last_seen(treeiter, last_seen)
        else:
            # Add a new device to the model
            treeiter = self.model.append([
                GdkPixbuf.Pixbuf.new_from_file(icon_path),
                icon_path,
                device_class,
                device_type,
                _(device_type),
                device_subtype,
                _(device_subtype),
                name,
                address,
                last_seen])
            self.devices[address] = treeiter
            self.settings.logText('Added new device "%s" (%s)' % (name,
                                                                  address),
                                  VERBOSE_LEVEL_MAX)
            # Execute notification for new devices
            if notify:
                # Play the sound notification
                if self.settings.get_value(Preferences.PLAY_SOUND):
                    self.audio_player.play_file(FILE_SOUND)
                # Show the graphical notification with icon
                if self.settings.get_value(Preferences.NOTIFICATION):
                    notification = Notify.Notification.new(
                          _('New bluetooth device detected'),
                          _('Name: %s\nAddress: %s') % (name or 'unknown',
                                                        address),
                          # Notification requires absolute paths
                          os.path.abspath(icon_path)
                    )
                    notification.set_urgency(Notify.Urgency.LOW)
                    notification.show()
        return treeiter

    def path_from_iter(self, treeiter):
        """Get path from iter"""
        return type(treeiter) is Gtk.TreeModelRow and treeiter.path or treeiter

    def get_model_data(self, treeiter, column):
        """Get the data from a column of a treeiter"""
        return self.model[self.path_from_iter(treeiter)][column]

    def set_model_data(self, treeiter, column, value):
        """Set the data in a column of a treeiter"""
        self.model[self.path_from_iter(treeiter)][column] = value

    def get_icon(self, treeiter):
        """Get the device icon"""
        return self.get_model_data(treeiter, self.__class__.COL_ICON_NAME)

    def set_icon(self, treeiter, value):
        """Set the device icon"""
        self.set_model_data(treeiter,
                            self.__class__.COL_ICON_NAME,
                            value)
        self.set_model_data(treeiter,
                            self.__class__.COL_ICON,
                            GdkPixbuf.Pixbuf.new_from_file(value))

    def get_name(self, treeiter):
        """Get the device name"""
        return self.get_model_data(treeiter, self.__class__.COL_NAME)

    def set_name(self, treeiter, value):
        """Set the device name"""
        self.set_model_data(treeiter, self.__class__.COL_NAME, value)

    def get_class(self, treeiter):
        """Get the device class"""
        return self.get_model_data(treeiter, self.__class__.COL_CLASS)

    def set_class(self, treeiter, value):
        """Set the device class"""
        self.set_model_data(treeiter, self.__class__.COL_CLASS, value)

    def get_type(self, treeiter):
        """Get the device type (untranslated)"""
        return self.get_model_data(treeiter, self.__class__.COL_TYPE)

    def set_type(self, treeiter, value):
        """Set the device type (untranslated)"""
        self.set_model_data(treeiter,
                            self.__class__.COL_TYPE,
                            value)
        self.set_model_data(treeiter,
                            self.__class__.COL_TYPE_TRANSLATED,
                            _(value))

    def get_subtype(self, treeiter):
        """Get the device sub type (untranslated)"""
        return self.get_model_data(treeiter, self.__class__.COL_SUBTYPE)

    def set_subtype(self, treeiter, value):
        """Set the device sub type (untranslated)"""
        self.set_model_data(treeiter,
                            self.__class__.COL_SUBTYPE,
                            value)
        self.set_model_data(treeiter,
                            self.__class__.COL_SUBTYPE_TRANSLATED,
                            _(value))

    def get_address(self, treeiter):
        """Get the device address"""
        return self.get_model_data(treeiter, self.__class__.COL_ADDRESS)

    def get_last_seen(self, treeiter):
        """Get the device last seen date"""
        return self.get_model_data(treeiter, self.__class__.COL_LASTSEEN)

    def set_last_seen(self, treeiter, value):
        """Set the device last seen date"""
        self.set_model_data(treeiter, self.__class__.COL_LASTSEEN, value)

    def __iter__(self):
        """Iter over the whole model rows"""
        for each in self.model:
            yield self.model[each.path]

    def __len__(self):
        """Get the devices count"""
        return len(self.model)
