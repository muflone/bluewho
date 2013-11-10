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
import os.path
import optparse
import time
import ConfigParser
from bluewho.functions import *
from bluewho.constants import *

class Settings(object):
  def __init__(self):
    self.settings = {}

    # Command line options and arguments
    parser = optparse.OptionParser(usage='usage: %prog [options]')
    parser.set_defaults(verbose_level=VERBOSE_LEVEL_NORMAL)
    parser.add_option('-v', '--verbose', dest='verbose_level',
                      action='store_const', const=VERBOSE_LEVEL_MAX,
                      help='show error and information messages')
    parser.add_option('-q', '--quiet', dest='verbose_level',
                      action='store_const', const=VERBOSE_LEVEL_QUIET,
                      help='hide error and information messages')
    (self.options, self.arguments) = parser.parse_args()
    # Parse settings from the configuration file
    self.config = ConfigParser.RawConfigParser()
    # Allow saving in case sensitive (useful for machine names)
    self.config.optionxform = str
    # Determine which filename to use for settings
    self.filename = FILE_SETTINGS_NEW
    if self.filename:
      self.logText('Loading settings from %s' % self.filename, VERBOSE_LEVEL_NORMAL)
      self.config.read(self.filename)

  def load(self):
    "Load window settings"
    if self.config.has_section(PREFS_SECTION_MAIN):
      self.logText('Retrieving window settings', VERBOSE_LEVEL_NORMAL)
      # Retrieve window position and size
      self.load_setting(PREFS_SECTION_MAIN, PREFS_OPTION_RESTORE_SIZE, bool, True)
      self.load_setting(PREFS_SECTION_MAIN, PREFS_OPTION_WINLEFT, int, None)
      self.load_setting(PREFS_SECTION_MAIN, PREFS_OPTION_WINTOP, int, None)
      self.load_setting(PREFS_SECTION_MAIN, PREFS_OPTION_WINWIDTH, int, None)
      self.load_setting(PREFS_SECTION_MAIN, PREFS_OPTION_WINHEIGHT, int, None)
    # Load preferences
    if self.config.has_section(PREFS_SECTION_STARTUP):
      self.logText('Retrieving startup preferences', VERBOSE_LEVEL_NORMAL)
      # Load startup preferences
      self.load_setting(PREFS_SECTION_STARTUP, PREFS_OPTION_STARTUPSCAN, bool, False)
    if self.config.has_section(PREFS_SECTION_SCAN):
      self.logText('Retrieving scan preferences', VERBOSE_LEVEL_NORMAL)
      # Load scan preferences
      self.load_setting(PREFS_SECTION_SCAN, PREFS_OPTION_RETRIEVE_NAMES, bool, False)
      self.load_setting(PREFS_SECTION_SCAN, PREFS_OPTION_RESOLVE_NAMES, bool, False)
      self.load_setting(PREFS_SECTION_SCAN, PREFS_OPTION_SHOW_LOCAL, bool, False)
    if self.config.has_section(PREFS_SECTION_NOTIFY):
      self.logText('Retrieving notify preferences', VERBOSE_LEVEL_NORMAL)
      # Load notify preferences
      self.load_setting(PREFS_SECTION_NOTIFY, PREFS_OPTION_NOTIFICATION, bool, False)
      self.load_setting(PREFS_SECTION_NOTIFY, PREFS_OPTION_PLAY_SOUND, bool, False)

  def load_setting(self, section, option, option_type, default_value):
    "Retrieve the setting from the file"
    value = default_value
    # Check if the option exists
    if self.config.has_option(section, option):
      if option_type is bool:
        # Get boolean value
        value = self.config.getboolean(section, option)
      elif option_type is int:
        # Get integer value
        value = self.config.getint(section, option)
      else:
        # Type unexpected
        assert False
    # Set value back in the configuration to allow its saving
    self.config.set(section, option, value)
    self.settings[option] = value
    return value

  def load_devices(self):
    "Return the devices list from the configuration file"
    devices = []
    if os.path.exists(FILE_SETTINGS_DEVICES):
      self.logText('Loading the devices list', VERBOSE_LEVEL_NORMAL)
      with open(FILE_SETTINGS_DEVICES, 'r') as f:
        # Each device is separated by a single line with >
        lines = f.read().split('\n>\n')
        for device in lines:
          if device:
            device = device.split('\n')
            devices.append({
              'address': device[0],
              'name': device[1],
              'class': int(device[2]),
              'lastseen': device[3],
            })
        f.close()
    return devices

  def save_devices(self, devices):
    "Save devices list to filename"
    if len(devices) > 0:
      self.logText('Saving the devices list', VERBOSE_LEVEL_NORMAL)
      with open(FILE_SETTINGS_DEVICES, 'w') as f:
        for device in devices:
          f.write('%s\n%s\n%d\n%s\n>\n' % (
            devices.get_address(device),
            devices.get_name(device),
            devices.get_class(device),
            devices.get_last_seen(device),
          ))
        f.close()
    elif os.path.exists(FILE_SETTINGS_DEVICES):
      self.logText('Deleting the devices list', VERBOSE_LEVEL_NORMAL)
      os.remove(FILE_SETTINGS_DEVICES)

  def get_value(self, option, default=None):
    "Get the value of an option"
    return self.settings.get(option, default)

  def set_sizes(self, winParent):
    "Save configuration for main window"
    # Main window settings section
    self.logText('Saving window settings', VERBOSE_LEVEL_NORMAL)
    if not self.config.has_section(PREFS_SECTION_MAIN):
      self.config.add_section(PREFS_SECTION_MAIN)
    # Window position
    position = winParent.get_position()
    self.config.set(PREFS_SECTION_MAIN, PREFS_OPTION_WINLEFT, position[0])
    self.config.set(PREFS_SECTION_MAIN, PREFS_OPTION_WINTOP, position[1])
    # Window size
    size = winParent.get_size()
    self.config.set(PREFS_SECTION_MAIN, PREFS_OPTION_WINWIDTH, size[0])
    self.config.set(PREFS_SECTION_MAIN, PREFS_OPTION_WINHEIGHT, size[1])

  def save(self):
    "Save the whole configuration"
    # Always save the settings in the new configuration file
    file_settings = open(FILE_SETTINGS_NEW, mode='w')
    self.logText('Saving settings to %s' % FILE_SETTINGS_NEW, VERBOSE_LEVEL_NORMAL)
    self.config.write(file_settings)
    file_settings.close()

  def logText(self, text, verbose_level=VERBOSE_LEVEL_NORMAL):
    "Print a text with current date and time based on verbose level"
    if verbose_level <= self.options.verbose_level:
      print '[%s] %s' % (time.strftime('%Y/%m/%d %H:%M:%S'), text)
