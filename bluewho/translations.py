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

import gettext
import locale

from bluewho.constants import APP_DOMAIN, DIR_LOCALE
from bluewho.localize import (store_message,
                              strip_colon,
                              strip_underline,
                              text)


# Load domain for translation
for module in (gettext, locale):
    module.bindtextdomain(APP_DOMAIN, DIR_LOCALE)
    module.textdomain(APP_DOMAIN)

# Import some translated messages from GTK+ domain
for message in ('About', 'General', 'Name', 'Type'):
    store_message(strip_colon(strip_underline(message)),
                  strip_colon(strip_underline(text(message=message,
                                                   gtk30=True))))

# Import some translated messages from GTK+ domain and context
for message in ('_Quit', ):
    store_message(strip_colon(strip_underline(message)),
                  strip_colon(strip_underline(text(message=message,
                                                   gtk30=True,
                                                   context='Stock label'))))
