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

# Please refer to Bluetooth specifications:
# https://www.bluetooth.com/specifications/assigned-numbers/
# https://specificationrefs.bluetooth.com/assigned-values/Appearance%20Values.pdf

class ServiceDeviceClasses(object):
    POSITIONING = 1       # 0x010000 >> 16
    NETWORKING = 2        # 0x020000 >> 16
    RENDERING = 4         # 0x040000 >> 16
    CAPTURING = 8         # 0x080000 >> 16
    OBJECT_TRANSFER = 16  # 0x100000 >> 16
    AUDIO = 32            # 0x200000 >> 16
    TELEPHONY = 64        # 0x400000 >> 16
    INFORMATION = 128     # 0x800000 >> 16
    # Dictionary for services descriptions
    SERVICE_CLASSES = {
      POSITIONING: 'positioning service',
      NETWORKING: 'networking service',
      RENDERING: 'rendering service',
      CAPTURING: 'capturing service',
      OBJECT_TRANSFER: 'object transfer service',
      AUDIO: 'audio service',
      TELEPHONY: 'telephony service',
      INFORMATION: 'information service',
    }
