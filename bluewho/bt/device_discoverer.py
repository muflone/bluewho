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

import dbus.exceptions

import bluezero.device
import bluezero.dbus_tools


class BluetoothDeviceDiscoverer():
    def __init__(self, adapter, timeout):
        self.adapter = adapter
        self.timeout = timeout

    def start(self) -> bool:
        """
        Start the bluetooth devices discovery

        :return: True if the discovery was successfull
        """
        print('scan started')
        try:
            self.adapter.start_discovery(timeout=self.timeout)
            result = True
        except dbus.exceptions.DBusException as error:
            print('scan aborted', error)
            result = False
        return result

    def stop(self) -> None:
        try:
            self.adapter.stop_discovery()
        except dbus.exceptions.DBusException:
            pass
        print('scan stopped')

    def get_devices(self) -> list[bluezero.device.Device]:
        """
        Get the detected devices list

        :return: list of detected device objects
        """
        results = []
        managed_objects = bluezero.dbus_tools.get_managed_objects()
        for path in managed_objects:
            address = bluezero.dbus_tools.get_device_address_from_dbus_path(
                path=path)
            if address:
                device = bluezero.device.Device(
                    adapter_addr=self.adapter.get_address(),
                    device_addr=address)
                results.append(device)
        return results
