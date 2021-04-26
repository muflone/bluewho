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

import pydbus


class BluetoothAdapter(object):
    def __init__(self, device_name):
        self.device_name = device_name

    def _get_dbus_interface(self):
        """Get a DBus interface to the bluetooth adapter"""
        return pydbus.SystemBus().get('org.bluez',
                                      '/org/bluez/%s' % self.device_name)

    def get_device_name(self):
        """Return the device name"""
        return self.device_name

    def get_name(self):
        """Return the adapter address"""
        return self._get_dbus_interface().Name

    def get_address(self):
        """Return the adapter address"""
        return self._get_dbus_interface().Address

    def is_powered(self):
        """Return the adapter powered status"""
        return self._get_dbus_interface().Powered

    def set_powered(self, status):
        """Set the adapter powered status"""
        self._get_dbus_interface().Powered = status
