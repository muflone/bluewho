##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices.
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

from bluetooth import DeviceDiscoverer

class BluetoothDeviceDiscoverer(DeviceDiscoverer):
  "Support for asynchronous detection"
  def __init__(self, new_device_cb):
    "Superclass constructor"
    DeviceDiscoverer.__init__(self)
    # Callback function to receive new discovered device
    self.new_device_cb = new_device_cb
    
  def pre_inquiry(self):
    "Scan is starting"
    self.done = False

  def device_discovered(self, address, device_class, name):
    "Call callback function for new discovered device"
    if self.new_device_cb:
      self.new_device_cb(name, address, device_class)

  def inquiry_complete(self):
    "Scan completed"
    self.done = True
