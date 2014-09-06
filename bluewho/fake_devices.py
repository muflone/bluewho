##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices.
#      Author: Fabio Castelli (Muflone) <webreg@vbsimple.net>
#   Copyright: 2009-2014 Fabio Castelli
#     License: GPL-2+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#  You should have received a copy of the GNU General Public License along
#  with this program; if not, write to the Free Software Foundation, Inc.,
#  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA
##

import random
from bluewho.constants import *
from bluewho.functions import *

class FakeDevices(object):
  def __init__(self):
    "Fake devices producer by reading the FILE_FAKE_DEVICES file"
    self.devices = []
    for line in readlines(FILE_FAKE_DEVICES):
      # Skip comments
      if '#' in line:
        line = line.split('#', 1)[0]
      if line:
        name, address, class_type = line.split(' | ', 2)
        # Generate random MAC address
        if address == '<RANDOM>':
          address = ':'.join(map(lambda number: '%02x' % number,
            (random.randint(0, 255) for octet in xrange(6)))).upper()
        class_type = int(class_type, class_type.startswith('0x') and 16 or 10)
        self.devices.append([name, address, class_type])

  def fetch_one(self):
    "Fetch a single fake device"
    return self.devices[random.randint(0, len(self.devices) - 1)]

  def fetch_max(self, count):
    "Fetch max count fake devices"
    return random.sample(self.devices, random.randint(0, 
      count <= len(self.devices) and count or len(self.devices)))

  def fetch_many(self):
    "Fetch a random number of fake devices"
    return random.sample(self.devices, random.randint(0, len(self.devices)))

  def fetch_all(self):
    "Fetch all the fake devices"
    return self.devices
