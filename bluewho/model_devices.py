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
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from bluewho.constants import *
from bluewho.functions import *

class ModelDevices(object):
  COL_ICON = 0
  COL_ICON_NAME = 1
  COL_CLASS = 2
  COL_TYPE = 3
  COL_TYPE_TRANSLATED = 4
  COL_SUBTYPE = 5
  COL_SUBTYPE_TRANSLATED = 6
  COL_NAME = 7
  COL_ADDRESS = 8
  COL_LASTSEEN = 9
  def __init__(self, model, settings, btsupport):
    self.model = model
    self.settings = settings
    self.btsupport = btsupport

  def clear(self):
    "Clear the model"
    return self.model.clear()

  def add_device(self, address, name, device_class, last_seen, notify):
    "Add a new device to the list and pops notification"
    minor_class, major_class, services_class = self.btsupport.get_classes(device_class)
    device_type = self.btsupport.get_device_type(major_class)
    icon_filename, device_subtype = self.btsupport.get_device_detail(
      major_class, minor_class)
    if device_subtype == 'adapter':
      device_type = 'adapter'
    icon_path = os.path.join(DIR_BT_ICONS, icon_filename)
    if not os.path.isfile(icon_path):
      icon_path = os.path.join(DIR_BT_ICONS, 'unknown.png')

    return self.model.append([
      GdkPixbuf.Pixbuf.new_from_file(icon_path),
      icon_path,
      device_class,
      device_type,
      _(device_type),
      device_subtype,
      _(device_subtype),
      name,
      address,
      last_seen
    ])
#  if notify:
#    if settings.get('play sound'):
#      playSound()
#    if settings.get('show notification'):
#      command = settings.get('notify cmd').replace('\\n', '\n') % {
#        'icon': iconPath, 'name': name and name or '', 'address': address }
#      proc = subprocess.Popen(command, shell=True)
#      proc.communicate()

  def path_from_iter(self, treeiter):
    "Get path from iter"
    return type(treeiter) is Gtk.TreeModelRow and treeiter.path or treeiter

  def get_model_data(self, treeiter, column):
    "Get the data from a column of a treeiter"
    return self.model[self.path_from_iter(treeiter)][column]

  def set_model_data(self, treeiter, column, value):
    "Set the data in a column of a treeiter"
    self.model[self.path_from_iter(treeiter)][column] = value

  def get_icon(self, treeiter):
    "Get the device icon"
    return self.get_model_data(treeiter, self.__class__.COL_ICON_NAME)

  def set_icon(self, treeiter, value):
    "Set the device icon"
    self.set_model_data(treeiter, self.__class__.COL_ICON_NAME, value)
    self.set_model_data(treeiter, self.__class__.COL_ICON, 
      GdkPixbuf.Pixbuf.new_from_file(value))

  def get_name(self, treeiter):
    "Get the device name"
    return self.get_model_data(treeiter, self.__class__.COL_NAME)

  def set_name(self, treeiter, value):
    "Set the device name"
    self.set_model_data(treeiter, self.__class__.COL_NAME, value)

  def get_class(self, treeiter):
    "Get the device class"
    return self.get_model_data(treeiter, self.__class__.COL_CLASS)

  def set_class(self, treeiter, value):
    "Set the device class"
    self.set_model_data(treeiter, self.__class__.COL_CLASS, value)

  def get_type(self, treeiter):
    "Get the device type (untranslated)"
    return self.get_model_data(treeiter, self.__class__.COL_TYPE)

  def set_type(self, treeiter, value):
    "Set the device type (untranslated)"
    self.set_model_data(treeiter, self.__class__.COL_TYPE, value)
    self.set_model_data(treeiter, self.__class__.COL_TYPE_TRANSLATED, _(value))

  def get_subtype(self, treeiter):
    "Get the device sub type (untranslated)"
    return self.get_model_data(treeiter, self.__class__.COL_SUBTYPE)

  def set_subtype(self, treeiter, value):
    "Set the device sub type (untranslated)"
    self.set_model_data(treeiter, self.__class__.COL_SUBTYPE, value)
    self.set_model_data(treeiter, self.__class__.COL_SUBTYPE_TRANSLATED, _(value))

  def get_address(self, treeiter):
    "Get the device address"
    return self.get_model_data(treeiter, self.__class__.COL_ADDRESS)

  def get_last_seen(self, treeiter):
    "Get the device last seen date"
    return self.get_model_data(treeiter, self.__class__.COL_LASTSEEN)

  def set_last_seen(self, treeiter, value):
    "Set the device last seen date"
    self.set_model_data(treeiter, self.__class__.COL_LASTSEEN, value)

  def __iter__(self):
    "Iter over the whole model rows"
    for each in self.model:
      yield self.model[each.path]

  def __len__(self):
    "Get the devices count"
    return len(self.model)
