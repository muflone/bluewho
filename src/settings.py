# -*- coding: utf-8 -*-
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

import os
import ConfigParser
import handlepaths
from gettext import gettext as _

config = None
confdir = os.path.join(os.path.expanduser('~/.config/bluewho'))
conffile = os.path.join(confdir, 'settings.conf')
devicesfiles = os.path.join(confdir, 'devices')
__sectionSettings = 'settings'
__sectionStartup = 'startup'
__sectionScan = 'scan'
__sectionNotify = 'notify'
__defSettings = None

if not os.path.exists(os.path.abspath(os.path.join(confdir, '..'))):
  os.mkdir(os.path.abspath(os.path.join(confdir, '..')))

if not os.path.exists(confdir):
  os.mkdir(confdir)

def load(filename=conffile):
  "Load settings from the configuration file"
  global config
  config = ConfigParser.RawConfigParser()
  loadDefaults()
  if os.path.exists(filename):
    config.read(filename)
  # Settings lookup is made upon __defSettings
  for setting in __defSettings.keys():
    # Add section if doesn't exist
    if not config.has_section(__defSettings[setting][2]):
      config.add_section(__defSettings[setting][2])
    if not config.has_option(__defSettings[setting][2], setting):
      config.set(__defSettings[setting][2], setting, str(__defSettings[setting][1]))

def loadDefaults():
  global __defSettings
  strbool = lambda value: value == 'True'
  __defSettings = {
    'startup scan': [strbool, False, __sectionStartup],
    'autoscan': [strbool, False, __sectionStartup],
    'restore size': [strbool, False, __sectionStartup],
    'retrieve names': [strbool, False, __sectionScan],
    'resolve names': [strbool, True, __sectionScan],
    'show local': [strbool, False, __sectionScan],
    'notify cmd': [str, 'notify-send -u low -i "%(icon)s" ' + \
      '"%s" ' % _('New bluetooth device detected') + \
      '"%(name)s\\n(%(address)s)"', __sectionNotify],
    'show notification': [strbool, True, __sectionNotify],
    'play sound': [strbool, False, __sectionNotify],
    'sound file': [str, handlepaths.getPath('data', 'newdevice.wav'), __sectionNotify],
    'scan duration': [int, 8, __sectionSettings],
    'flush cache': [strbool, True, __sectionSettings],
    'window width': [int, 570, __sectionStartup],
    'window height': [int, 360, __sectionStartup],
    'window left': [int, 200, __sectionStartup],
    'window top': [int, 100, __sectionStartup],
}

def save(filename=conffile, clearDefaults=False):
  "Save settings into the configuration file"
  file = open(filename, mode='w')
  if clearDefaults:
    for setting in __defSettings.keys():
      if config.has_option(__defSettings[setting][2], setting):
        if get(setting) == __defSettings[setting][1]:
          config.remove_option(__defSettings[setting][2], setting)
  config.write(file)
  file.close

def get(setting):
  "Returns a specified setting from the configuration or default values"
  if config.has_option(__defSettings[setting][2], setting):
    return __defSettings[setting][0](config.get(__defSettings[setting][2], setting))
  elif __defSettings.has_key(setting):
    return __defSettings[setting][1]
  else:
    print 'unknown setting: %s' % setting

def default(setting):
  "Returns the default value for a specified setting"
  if __defSettings.has_key(setting):
    return __defSettings[setting][1]

def set(setting, value):
  "Sets a specific setting to the value."
  config.set(__defSettings[setting][2], setting, str(value))
