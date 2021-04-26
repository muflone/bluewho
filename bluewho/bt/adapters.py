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

from xml.etree import ElementTree

import pydbus

from .adapter import BluetoothAdapter


class BluetoothAdapters(object):
    def get_adapters(self):
        """Get a list of local adapters"""
        dbus_manager = pydbus.SystemBus().get('org.bluez')
        xml = ElementTree.fromstring(dbus_manager.Introspect())
        adapters = [BluetoothAdapter(node.attrib['name'])
                    for node in xml
                    if node.tag == 'node']
        return adapters
