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

import os
import os.path
import optparse
import time
import configparser

from bluewho.constants import (FILE_SETTINGS_DEVICES,
                               FILE_SETTINGS_NEW,
                               VERBOSE_LEVEL_QUIET,
                               VERBOSE_LEVEL_NORMAL,
                               VERBOSE_LEVEL_MAX)


class Sections(object):
    MAIN = 'main window'
    STARTUP = 'startup'
    SCAN = 'scan'
    NOTIFY = 'notify'


class Preferences(object):
    RESTORE_SIZE = 'restore size'
    WINLEFT = 'left'
    WINTOP = 'top'
    WINWIDTH = 'width'
    WINHEIGHT = 'height'
    STARTUPSCAN = 'startup scan'
    RETRIEVE_NAMES = 'retrieve names'
    RESOLVE_NAMES = 'resolve names'
    SCAN_SPEED = 'scan speed'
    SHOW_LOCAL = 'show local'
    NOTIFICATION = 'show notification'
    PLAY_SOUND = 'play sound'


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
        self.config = configparser.RawConfigParser()
        # Allow saving in case sensitive (useful for machine names)
        self.config.optionxform = str
        # Determine which filename to use for settings
        self.filename = FILE_SETTINGS_NEW
        if self.filename:
            self.logText('Loading settings from %s' % self.filename,
                         VERBOSE_LEVEL_NORMAL)
            self.config.read(self.filename)

    def load(self):
        """Load preferences from configuration file"""
        # Load window preferences
        self.logText('Loading window settings', VERBOSE_LEVEL_NORMAL)
        if not self.config.has_section(Sections.MAIN):
            self.config.add_section(Sections.MAIN)
        self.load_setting(section=Sections.MAIN,
                          option=Preferences.RESTORE_SIZE,
                          option_type=bool,
                          default_value=True)
        self.load_setting(section=Sections.MAIN,
                          option=Preferences.WINLEFT,
                          option_type=int,
                          default_value=0)
        self.load_setting(section=Sections.MAIN,
                          option=Preferences.WINTOP,
                          option_type=int,
                          default_value=0)
        self.load_setting(section=Sections.MAIN,
                          option=Preferences.WINWIDTH,
                          option_type=int,
                          default_value=0)
        self.load_setting(section=Sections.MAIN,
                          option=Preferences.WINHEIGHT,
                          option_type=int,
                          default_value=0)
        # Load startup preferences
        self.logText('Loading startup preferences', VERBOSE_LEVEL_NORMAL)
        if not self.config.has_section(Sections.STARTUP):
            self.config.add_section(Sections.STARTUP)
        self.load_setting(section=Sections.STARTUP,
                          option=Preferences.STARTUPSCAN,
                          option_type=bool,
                          default_value=False)
        # Load scan preferences
        self.logText('Loading scan preferences', VERBOSE_LEVEL_NORMAL)
        if not self.config.has_section(Sections.SCAN):
            self.config.add_section(Sections.SCAN)
        self.load_setting(section=Sections.SCAN,
                          option=Preferences.SCAN_SPEED,
                          option_type=int,
                          default_value=14)
        self.load_setting(section=Sections.SCAN,
                          option=Preferences.RETRIEVE_NAMES,
                          option_type=bool,
                          default_value=False)
        self.load_setting(section=Sections.SCAN,
                          option=Preferences.RESOLVE_NAMES,
                          option_type=bool,
                          default_value=True)
        self.load_setting(section=Sections.SCAN,
                          option=Preferences.SHOW_LOCAL,
                          option_type=bool,
                          default_value=True)
        # Load notify preferences
        self.logText('Loading notify preferences', VERBOSE_LEVEL_NORMAL)
        if not self.config.has_section(Sections.NOTIFY):
            self.config.add_section(Sections.NOTIFY)
        self.load_setting(section=Sections.NOTIFY,
                          option=Preferences.NOTIFICATION,
                          option_type=bool,
                          default_value=True)
        self.load_setting(section=Sections.NOTIFY,
                          option=Preferences.PLAY_SOUND,
                          option_type=bool,
                          default_value=True)

    def load_setting(self, section, option, option_type, default_value):
        """Retrieve the setting from the file"""
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
        """Return the devices list from the configuration file"""
        devices = []
        if os.path.exists(FILE_SETTINGS_DEVICES):
            self.logText('Loading the devices list', VERBOSE_LEVEL_NORMAL)
            with open(FILE_SETTINGS_DEVICES, 'r') as file:
                # Each device is separated by a single line with >
                lines = file.read().split('\n>\n')
                for device in lines:
                    if device:
                        device = device.split('\n')
                        devices.append({
                          'address': device[0],
                          'name': device[1],
                          'class': int(device[2],
                                       device[2].startswith('0x')
                                       and 16 or 10),
                          'lastseen': device[3]})
        return devices

    def save_devices(self, devices):
        """Save devices list to filename"""
        if len(devices) > 0:
            self.logText('Saving the devices list', VERBOSE_LEVEL_NORMAL)
            with open(FILE_SETTINGS_DEVICES, 'w') as file:
                for device in devices:
                    file.write('%s\n%s\n%s\n%s\n>\n' % (
                        devices.get_address(device),
                        devices.get_name(device),
                        hex(devices.get_class(device)),
                        devices.get_last_seen(device)))
        elif os.path.exists(FILE_SETTINGS_DEVICES):
            self.logText('Deleting the devices list', VERBOSE_LEVEL_NORMAL)
            os.remove(FILE_SETTINGS_DEVICES)

    def get_value(self, option, default=None):
        """Get the value of an option"""
        return self.settings.get(option, default)

    def set_value(self, option, value):
        """Set the value for an option"""
        self.settings[option] = value
        # Search the option in all the sections of the configuration file
        for section in self.config.sections():
            if self.config.has_option(section, option):
                # Set the value in the configuration file
                self.config.set(section, option, value)
                break

    def set_sizes(self, parent):
        """Save configuration for main window"""
        # Main window settings section
        self.logText('Saving window settings', VERBOSE_LEVEL_NORMAL)
        if not self.config.has_section(Sections.MAIN):
            self.config.add_section(Sections.MAIN)
        # Window position
        position = parent.get_position()
        self.config.set(Sections.MAIN, Preferences.WINLEFT, position[0])
        self.config.set(Sections.MAIN, Preferences.WINTOP, position[1])
        # Window size
        size = parent.get_size()
        self.config.set(Sections.MAIN, Preferences.WINWIDTH, size[0])
        self.config.set(Sections.MAIN, Preferences.WINHEIGHT, size[1])

    def save(self):
        """Save the whole configuration"""
        # Always save the settings in the new configuration file
        with open(FILE_SETTINGS_NEW, mode='w') as file:
            self.logText('Saving settings to %s' % FILE_SETTINGS_NEW,
                         VERBOSE_LEVEL_NORMAL)
            self.config.write(file)

    def logText(self, text, verbose_level=VERBOSE_LEVEL_NORMAL):
        """Print a text with current date and time based on verbose level"""
        if verbose_level <= self.options.verbose_level:
            print('[%s] %s' % (time.strftime('%Y/%m/%d %H:%M:%S'), text))
