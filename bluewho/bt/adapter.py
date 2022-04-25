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

class BluetoothAdapter(object):
    def __init__(self, adapter):
        self.adapter = adapter

    def get_device_name(self):
        """Return the device name"""
        return self.adapter.path.replace('/org/bluez/', '')

    def get_name(self):
        """Return the adapter address"""
        return str(self.adapter.name)

    def get_address(self):
        """Return the adapter address"""
        return str(self.adapter.address)

    def is_powered(self):
        """Return the adapter powered status"""
        return bool(self.adapter.powered)

    def set_powered(self, status):
        """Set the adapter powered status"""
        self.adapter.powered = status

    def start_discovery(self, timeout):
        """
        Start devices discovery
        """
        self.adapter.nearby_discovery(timeout=timeout)

    def stop_discovery(self):
        """
        Stop devices discovery
        """
        self.adapter.stop_discovery()
