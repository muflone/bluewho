#!/usr/bin/env python3
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

import gettext
import locale
from bluewho.settings import Settings
from bluewho.btsupport import BluetoothSupport
from bluewho.app import Application
from bluewho.constants import DOMAIN_NAME, DIR_LOCALE

if __name__ == '__main__':
    # Load domain for translation
    for module in (gettext, locale):
        module.bindtextdomain(DOMAIN_NAME, DIR_LOCALE)
        module.textdomain(DOMAIN_NAME)

    # Load the settings from the configuration file
    settings = Settings()
    settings.load()

    # Create BluetoothSupport instance
    btsupport = BluetoothSupport()
    # Start the application
    app = Application(settings, btsupport)
    app.run(None)
