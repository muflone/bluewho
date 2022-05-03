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

DEFAULT_VALUES = {}

SECTION_NOTIFY = 'notify'
SECTION_SCAN = 'scan'
SECTION_STARTUP = 'startup'

PREFERENCES_NOTIFICATION = 'show notification'
DEFAULT_VALUES[PREFERENCES_NOTIFICATION] = (SECTION_NOTIFY, True)

PREFERENCES_PLAY_SOUND = 'play sound'
DEFAULT_VALUES[PREFERENCES_PLAY_SOUND] = (SECTION_NOTIFY, True)

PREFERENCES_SCAN_SPEED = 'scan speed'
DEFAULT_VALUES[PREFERENCES_SCAN_SPEED] = (SECTION_SCAN, 4)

PREFERENCES_SHOW_LOCAL = 'show local'
DEFAULT_VALUES[PREFERENCES_SHOW_LOCAL] = (SECTION_SCAN, True)

PREFERENCES_STARTUPSCAN = 'startup scan'
DEFAULT_VALUES[PREFERENCES_STARTUPSCAN] = (SECTION_STARTUP, False)


class Preferences(object):
    def __init__(self, settings):
        """Load settings into preferences"""
        self.settings = settings
        self.options = {}
        for option in DEFAULT_VALUES.keys():
            section, default = DEFAULT_VALUES[option]
            # Save the default value
            if isinstance(default, bool):
                self.options[option] = self.settings.get_boolean(
                    section, option, default)
            elif isinstance(default, int):
                self.options[option] = self.settings.get_int(
                    section, option, default)
            else:
                self.options[option] = self.settings.get(
                    section, option, default)

    def get(self, option):
        """Returns a preferences option"""
        return self.options[option]

    def set(self, option, value):
        """Set a preferences option"""
        self.options[option] = value
        if option in DEFAULT_VALUES:
            section, default = DEFAULT_VALUES[option]
            if isinstance(default, bool):
                self.settings.set_boolean(section, option, value)
            elif isinstance(default, int):
                self.settings.set_int(section, option, value)
            else:
                self.settings.set(section, option, value)
