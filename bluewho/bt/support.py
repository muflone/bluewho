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

import bluezero.dbus_tools

import dbus

from bluewho.bt.major_device_classes import MajorDeviceClasses
from bluewho.constants import FILE_BT_CLASSES
from bluewho.functions import readlines


class BluetoothSupport(object):
    def __init__(self):
        # Load classes from file FILE_BT_CLASSES
        self.classes = {}
        for line in readlines(FILE_BT_CLASSES):
            # Skip comments
            if '#' in line:
                line = line.split('#', 1)[0]
            # Skip empty lines
            line = line.strip()
            if line:
                # File format:
                # Major class | Minor class | PNG Image | Description
                major_class, minor_class, image_path, description = line.split(
                    ' | ', 3)
                major_class = int(major_class)
                minor_class = int(minor_class)
                image_path = image_path.strip()
                # New major class
                if major_class not in self.classes:
                    self.classes[major_class] = {}
                # Add minor class with image and description
                self.classes[major_class][minor_class] = (image_path,
                                                          description)

    def get_classes(self, device_class):
        """Return device minor, major class and services class"""
        # Bits 02-07 Minor class bitwise
        minor_class = (device_class & 0xff) >> 2
        # Bits 08-12 Major class bitwise
        major_class = (device_class >> 8) & 0x1f
        # Bits 16-23 Service class
        services_class = (device_class >> 16)
        return minor_class, major_class, services_class

    def get_device_type(self, major_class):
        """Return the device major class"""
        if major_class not in MajorDeviceClasses.CLASSES:
            # Fallback to unknown class
            major_class = MajorDeviceClasses.UNKNOWN
        return MajorDeviceClasses.CLASSES[major_class]

    def get_device_detail(self, major_class, minor_class):
        """Return the device detail type or fallback to the unknown device"""
        return self.classes.get(major_class,
                                MajorDeviceClasses.UNKNOWN).get(
            minor_class,
            self.classes[MajorDeviceClasses.UNKNOWN][0])

    def is_bluez_available(self):
        """Check if bluez is available"""
        try:
            bluezero.dbus_tools.get_managed_objects()
            result = True
        except dbus.exceptions.DBusException:
            result = False
        return result
