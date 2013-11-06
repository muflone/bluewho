##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices.
#      Author: Fabio Castelli (Muflone) <webreg@vbsimple.net>
#   Copyright: 2009-2013 Fabio Castelli
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

import os.path
from gi.repository import GdkPixbuf
from bluewho.constants import *
from bluewho.functions import *

class ModelServices(object):
  COL_NAME = 0
  COL_PROTOCOL = 1
  COL_CHANNEL = 2
  def __init__(self, model, settings, btsupport):
    self.model = model
    self.settings = settings
    self.btsupport = btsupport

  def clear(self):
    "Clear the model"
    return self.model.clear()

  def add_service(self, service, protocol, channel):
    "Add a new service to the list"
    return self.model.append([
      service,
      protocol,
      name
    ])
