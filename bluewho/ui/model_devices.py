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
                               DIR_ICONS,
                               FILE_SOUND)
from bluewho.functions import get_current_time
from bluewho.localize import _
from bluewho.models.abstract import ModelAbstract
from bluewho.models.device_info import DeviceInfo
from bluewho.settings import (PREFERENCES_NOTIFICATION,
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

    def __init__(self, model, settings, btsupport):
        super(self.__class__, self).__init__(model)
        self.settings = settings
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

    def add_data(self, device: DeviceInfo):
        """Add or update a model row"""
        super(self.__class__, self).add_data(device)
        if device.address not in self.rows:
            # Add a new row if it doesn't exist
            minor, major, services_class = self.btsupport.get_classes(
                device.device_class)
            device_type = self.btsupport.get_device_type(major)
            icon_filename, device_subtype = self.btsupport.get_device_detail(
                major, minor)
            if device_subtype == 'adapter':
                device_type = 'adapter'
            icon_path = DIR_ICONS / icon_filename
            if not icon_path.is_file():
                icon_filename = 'unknown.png'
                icon_path = DIR_ICONS / icon_filename
            # Replace None with empty string in name
            if device.name is None:
                device.name = ''
            if device.address in self.rows:
                # Update the existing device in the model
                treeiter = self.rows[device.address]
                # Update icon
                old_value = self.get_icon(treeiter)
                if icon_path != old_value:
                    logging.debug(f'Updated device "{device.name}" icon '
                                  f'from {os.path.basename(old_value)} '
                                  f'to {os.path.basename(icon_path)}')
                    self.set_icon(treeiter, icon_path)
                # Update device name
                old_value = self.get_name(treeiter)
                if device.name and device.name != old_value:
                    logging.debug(f'Updated device "{device.name}" name '
                                  f'from "{old_value}" to "{device.name}"')
                    self.set_name(treeiter, device.name)
                # Update device class
                old_value = self.get_class(treeiter)
                if device.device_class != old_value:
                    logging.debug(f'Updated device "{device.name}" class '
                                  f'from {old_value} to {device.device_class}')
                    self.set_class(treeiter, device.device_class)
                # Update device type
                old_value = self.get_type(treeiter)
                if device_type != old_value:
                    logging.debug(f'Updated device "{device.name}" type '
                                  f'from {old_value} to {device_type}')
                    self.set_type(treeiter, device_type)
                # Update device subtype
                old_value = self.get_subtype(treeiter)
                if device_subtype != old_value:
                    logging.debug(f'Updated device "{device.name}" subtype '
                                  f'from {old_value} to {device_subtype}')
                    self.set_subtype(treeiter, device_subtype)
                # Update device last seen time (always)
                self.set_last_seen(treeiter,
                                   device.last_seen or get_current_time())
            else:
                # Add a new device to the model
                treeiter = self.model.append([
                    device.address,
                    GdkPixbuf.Pixbuf.new_from_file(str(icon_path)),
                    str(icon_path),
                    device.device_class,
                    device_type,
                    _(device_type),
                    device_subtype,
                    _(device_subtype),
                    device.name,
                    device.last_seen or get_current_time()])
                self.rows[device.address] = treeiter
                logging.debug(f'Added new device "{device.name}" '
                              f'({device.address})')
                # Execute notification for new devices
                if device.notify:
                    # Play the sound notification
                    if self.settings.get_preference(
                            option=PREFERENCES_PLAY_SOUND):
                        self.audio_player.play_file(FILE_SOUND)
                    # Show the graphical notification with icon
                    if self.settings.get_preference(
                            option=PREFERENCES_NOTIFICATION):
                        notification = Notify.Notification.new(
                            _('New bluetooth device detected'),
                            _('Name: {NAME}\nAddress: {ADDRESS}').format(
                                NAME=device.name or 'unknown',
                                ADDRESS=device.address),
                            # Notification requires absolute paths
                            str(icon_path.resolve()))
                        notification.set_urgency(Notify.Urgency.LOW)
                        notification.show()
        else:
            # Update existing row
            treeiter = self.rows[device.address]
            self.set_last_seen(treeiter,
                               device.last_seen or get_current_time())
            logging.debug(f'Updated device "{device.name}" '
                          f'({device.address})')
        return treeiter

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
        """Get the device subtype (untranslated)"""
        return self.get_data(treeiter, self.COL_SUBTYPE)

    def set_subtype(self, treeiter, value):
        """Set the device subtype (untranslated)"""
        self.set_data(treeiter, self.COL_SUBTYPE, value)
        self.set_data(treeiter, self.COL_SUBTYPE_TRANSLATED, _(value))

    def get_last_seen(self, treeiter):
        """Get the device last seen date"""
        return self.get_data(treeiter, self.COL_LASTSEEN)

    def set_last_seen(self, treeiter, value):
        """Set the device last seen date"""
        self.set_data(treeiter, self.COL_LASTSEEN, value)
