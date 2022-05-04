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

import logging
import os.path

from gi.repository import GdkPixbuf
from gi.repository import Notify

from bluewho.audio_player import AudioPlayer
from bluewho.constants import (APP_NAME,
                               DIR_BT_ICONS,
                               FILE_SOUND)
from bluewho.functions import _
from bluewho.models.abstract import ModelAbstract
from bluewho.models.device_info import DeviceInfo
from bluewho.preferences import (PREFERENCES_NOTIFICATION,
                                 PREFERENCES_PLAY_SOUND)


class ModelDevices(ModelAbstract):
    COL_ICON = 1
    COL_ICON_NAME = 2
    COL_CLASS = 3
    COL_TYPE = 4
    COL_TYPE_TRANSLATED = 5
    COL_SUBTYPE = 6
    COL_SUBTYPE_TRANSLATED = 7
    COL_NAME = 8
    COL_LASTSEEN = 9

    def __init__(self, model, settings, preferences, btsupport):
        super(self.__class__, self).__init__(model)
        self.settings = settings
        self.preferences = preferences
        self.btsupport = btsupport
        self.audio_player = AudioPlayer()
        Notify.init(APP_NAME)

    def destroy(self):
        """Destroy any pending objects"""
        self.clear()
        self.model = None
        self.settings = None
        self.btsupport = None
        self.audio_player = None

    def add_data(self, item: DeviceInfo):
        """Add or update a model row"""
        super(self.__class__, self).add_data(item)
        if item.address not in self.rows:
            # Add a new row if it doesn't exist
            minor, major, services_class = self.btsupport.get_classes(
                item.device_class)
            device_type = self.btsupport.get_device_type(major)
            icon_filename, device_subtype = self.btsupport.get_device_detail(
                major, minor)
            if device_subtype == 'adapter':
                device_type = 'adapter'
            icon_path = os.path.join(DIR_BT_ICONS, icon_filename)
            if not os.path.isfile(icon_path):
                icon_filename = 'unknown.png'
                icon_path = os.path.join(DIR_BT_ICONS, icon_filename)
            # Replace None with empty string in name
            if item.name is None:
                item.name = ''
            if item.address in self.rows:
                # Update the existing device in the model
                treeiter = self.rows[item.address]
                # Update icon
                old_value = self.get_icon(treeiter)
                if icon_path != old_value:
                    logging.debug(f'Updated device "{item.name}" icon '
                                  f'from {os.path.basename(old_value)} '
                                  f'to {os.path.basename(icon_path)}')
                    self.set_icon(treeiter, icon_path)
                # Update device name
                old_value = self.get_name(treeiter)
                if item.name and item.name != old_value:
                    logging.debug(f'Updated device "{item.name}" name '
                                  f'from "{old_value}" to "{item.name}"')
                    self.set_name(treeiter, item.name)
                # Update device class
                old_value = self.get_class(treeiter)
                if item.device_class != old_value:
                    logging.debug(f'Updated device "{item.name}" class '
                                  f'from {old_value} to {item.device_class}')
                    self.set_class(treeiter, item.device_class)
                # Update device type
                old_value = self.get_type(treeiter)
                if device_type != old_value:
                    logging.debug(f'Updated device "{item.name}" type '
                                  f'from {old_value} to {device_type}')
                    self.set_type(treeiter, device_type)
                # Update device subtype
                old_value = self.get_subtype(treeiter)
                if device_subtype != old_value:
                    logging.debug(f'Updated device "{item.name}" subtype '
                                  f'from {old_value} to {device_subtype}')
                    self.set_subtype(treeiter, device_subtype)
                # Update device last seen time (always)
                self.set_last_seen(treeiter, item.last_seen)
            else:
                # Add a new device to the model
                treeiter = self.model.append([
                    item.address,
                    GdkPixbuf.Pixbuf.new_from_file(icon_path),
                    icon_path,
                    item.device_class,
                    device_type,
                    _(device_type),
                    device_subtype,
                    _(device_subtype),
                    item.name,
                    item.last_seen])
                self.rows[item.address] = treeiter
                logging.debug(f'Added new device "{item.name}" '
                              f'({item.address})')
                # Execute notification for new devices
                if item.notify:
                    # Play the sound notification
                    if self.preferences.get(PREFERENCES_PLAY_SOUND):
                        self.audio_player.play_file(FILE_SOUND)
                    # Show the graphical notification with icon
                    if self.preferences.get(PREFERENCES_NOTIFICATION):
                        notification = Notify.Notification.new(
                            _('New bluetooth device detected'),
                            _('Name: {NAME}\nAddress: {ADDRESS}').format(
                                NAME=item.name or 'unknown',
                                ADDRESS=item.address
                            ),
                            # Notification requires absolute paths
                            os.path.abspath(icon_path)
                        )
                        notification.set_urgency(Notify.Urgency.LOW)
                        notification.show()
        else:
            # Update existing row
            treeiter = self.rows[item.address]
            self.set_last_seen(treeiter, item.last_seen)
            logging.debug(f'Updated device "{item.name}" '
                          f'({item.address})')
        return treeiter

    def add_device(self, address, name, device_class, last_seen, notify):
        """Add a new device to the list and pops notification"""
        self.add_data(DeviceInfo(address=address,
                                 name=name,
                                 device_class=device_class,
                                 last_seen=last_seen,
                                 notify=notify))

    def get_icon(self, treeiter):
        """Get the device icon"""
        return self.get_data(treeiter, self.COL_ICON_NAME)

    def set_icon(self, treeiter, value):
        """Set the device icon"""
        self.set_data(treeiter, self.COL_ICON_NAME, value)
        self.set_data(treeiter, self.COL_ICON,
                      GdkPixbuf.Pixbuf.new_from_file(value))

    def get_name(self, treeiter):
        """Get the device name"""
        return self.get_data(treeiter, self.COL_NAME)

    def set_name(self, treeiter, value):
        """Set the device name"""
        self.set_data(treeiter, self.COL_NAME, value)

    def get_class(self, treeiter):
        """Get the device class"""
        return self.get_data(treeiter, self.COL_CLASS)

    def set_class(self, treeiter, value):
        """Set the device class"""
        self.set_data(treeiter, self.COL_CLASS, value)

    def get_type(self, treeiter):
        """Get the device type (untranslated)"""
        return self.get_data(treeiter, self.COL_TYPE)

    def set_type(self, treeiter, value):
        """Set the device type (untranslated)"""
        self.set_data(treeiter, self.COL_TYPE, value)
        self.set_data(treeiter, self.COL_TYPE_TRANSLATED, _(value))

    def get_subtype(self, treeiter):
        """Get the device sub type (untranslated)"""
        return self.get_data(treeiter, self.COL_SUBTYPE)

    def set_subtype(self, treeiter, value):
        """Set the device sub type (untranslated)"""
        self.set_data(treeiter, self.COL_SUBTYPE, value)
        self.set_data(treeiter, self.COL_SUBTYPE_TRANSLATED, _(value))

    def get_last_seen(self, treeiter):
        """Get the device last seen date"""
        return self.get_data(treeiter, self.COL_LASTSEEN)

    def set_last_seen(self, treeiter, value):
        """Set the device last seen date"""
        self.set_data(treeiter, self.COL_LASTSEEN, value)
