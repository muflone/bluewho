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

class MajorDeviceClasses(object):
    UNKNOWN = 0
    COMPUTER = 1
    PHONE = 2
    NETWORK = 3
    AUDIOVIDEO = 4
    PERIPHERAL = 5
    IMAGING = 6
    MISCELLANEOUS = 7
    TOY = 8
    HEALTH = 9
    # Dictionary for classes descriptions
    CLASSES = {
      UNKNOWN: 'unknown',
      COMPUTER: 'computer',
      PHONE: 'phone',
      NETWORK: 'network',
      AUDIOVIDEO: 'audio-video',
      PERIPHERAL: 'peripheral',
      IMAGING: 'imaging',
      MISCELLANEOUS: 'miscellaneous',
      TOY: 'toy',
      HEALTH: 'health',
    }
