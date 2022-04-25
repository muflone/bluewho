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

import bluezero.device

import dbus


class BluetoothDevice(object):
    def __init__(self, device: bluezero.device.Device):
        try:
            self.name = device.name
        except dbus.exceptions.DBusException:
            self.name = None

        try:
            self.alias = device.alias
        except dbus.exceptions.DBusException:
            self.alias = None

        try:
            self.address = device.address
        except dbus.exceptions.DBusException:
            self.address = None

        try:
            self.device_class = device.bt_class
        except dbus.exceptions.DBusException:
            self.device_class = None
