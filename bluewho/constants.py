##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices.
#      Author: Fabio Castelli (Muflone) <muflone@vbsimple.net>
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

import sys
import os.path
from xdg import BaseDirectory

# Application constants
APP_NAME = 'BlueWho'
APP_VERSION = '0.2.2'
APP_DESCRIPTION = 'Information and notification of new discovered bluetooth devices'
APP_ID = 'bluewho.muflone.com'
APP_URL = 'http://www.muflone.com/bluewho'
APP_AUTHOR = 'Fabio Castelli'
APP_AUTHOR_EMAIL = 'muflone@vbsimple.net'
APP_COPYRIGHT = 'Copyright 2009-2014 %s' % APP_AUTHOR
# Other constants
DOMAIN_NAME = 'bluewho'
VERBOSE_LEVEL_QUIET = 0
VERBOSE_LEVEL_NORMAL = 1
VERBOSE_LEVEL_MAX = 2
USE_FAKE_DEVICES = False

# Paths constants
# If there's a file data/bluewho.png then the shared data are searched
# in relative paths, else the standard paths are used
if os.path.isfile(os.path.join('data', 'bluewho.png')):
  DIR_PREFIX = '.'
  DIR_LOCALE = os.path.join(DIR_PREFIX, 'locale')
  DIR_DOCS = os.path.join(DIR_PREFIX, 'doc')
else:
  DIR_PREFIX = os.path.join(sys.prefix, 'share', 'bluewho')
  DIR_LOCALE = os.path.join(sys.prefix, 'share', 'locale')
  DIR_DOCS = os.path.join(sys.prefix, 'share', 'doc', 'bluewho')
# Set the paths for the folders
DIR_DATA = os.path.join(DIR_PREFIX, 'data')
DIR_UI = os.path.join(DIR_PREFIX, 'ui')
DIR_SETTINGS = BaseDirectory.save_config_path(DOMAIN_NAME)
DIR_BT_ICONS = os.path.join(DIR_DATA, 'icons')
# Set the paths for the UI files
FILE_UI_MAIN = os.path.join(DIR_UI, 'main.glade')
FILE_UI_ABOUT = os.path.join(DIR_UI, 'about.glade')
FILE_UI_SERVICES = os.path.join(DIR_UI, 'services.glade')
FILE_UI_PREFERENCES = os.path.join(DIR_UI, 'preferences.glade')
FILE_UI_APPMENU = os.path.join(DIR_UI, 'appmenu.ui')
# Set the paths for the data files
FILE_ICON = os.path.join(DIR_DATA, 'bluewho.png')
FILE_TRANSLATORS = os.path.join(DIR_DOCS, 'translators')
FILE_LICENSE = os.path.join(DIR_DOCS, 'license')
FILE_RESOURCES = os.path.join(DIR_DOCS, 'resources')
FILE_BT_CLASSES = os.path.join(DIR_DATA, 'classes.txt')
FILE_FAKE_DEVICES = os.path.join(DIR_DATA, 'fake_devices.txt')
FILE_SOUND = os.path.join(DIR_DATA, 'newdevice.wav')
# Set the paths for configuration files
FILE_SETTINGS_NEW = os.path.join(DIR_SETTINGS, 'settings.conf')
FILE_SETTINGS_DEVICES = os.path.join(DIR_SETTINGS, 'devices')
