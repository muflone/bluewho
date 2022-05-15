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

import logging

from gi.repository.GdkPixbuf import Pixbuf

from bluewho.constants import (APP_AUTHOR,
                               APP_AUTHOR_EMAIL,
                               APP_NAME,
                               APP_COPYRIGHT,
                               APP_DESCRIPTION,
                               APP_URL,
                               APP_VERSION,
                               FILE_ICON,
                               FILE_LICENSE,
                               FILE_RESOURCES,
                               FILE_TRANSLATORS)
from bluewho.functions import readlines
from bluewho.localize import _
from bluewho.ui.base import UIBase


class DialogAbout(UIBase):
    def __init__(self, parent):
        super().__init__(filename='about.ui')
        logging.debug(f'{self.__class__.__name__} init')
        # Retrieve the translators list
        translators = []
        for line in readlines(FILE_TRANSLATORS, False):
            if ':' in line:
                line = line.split(':', 1)[1]
            line = line.replace('(at)', '@').strip()
            if line not in translators:
                translators.append(line)
        # Set various properties
        self.ui.dialog.set_program_name(APP_NAME)
        self.ui.dialog.set_version(_('Version {VERSION}').format(
            VERSION=APP_VERSION))
        self.ui.dialog.set_comments(APP_DESCRIPTION)
        self.ui.dialog.set_website(APP_URL)
        self.ui.dialog.set_copyright(APP_COPYRIGHT)
        # Prepare lists for authors and contributors
        authors = [f'{APP_AUTHOR} <{APP_AUTHOR_EMAIL}>']
        self.ui.dialog.set_authors(authors)
        self.ui.dialog.set_license('\n'.join(readlines(FILE_LICENSE, True)))
        self.ui.dialog.set_translator_credits('\n'.join(translators))
        # Retrieve the external resources links
        for line in readlines(FILE_RESOURCES, False):
            resource_type, resource_url = line.split(':', 1)
            self.ui.dialog.add_credit_section(resource_type, (resource_url,))
        icon_logo = Pixbuf.new_from_file(str(FILE_ICON))
        self.ui.dialog.set_logo(icon_logo)
        self.ui.dialog.set_transient_for(parent)

    def show(self):
        """Show the About dialog"""
        logging.debug(f'{self.__class__.__name__} show')
        self.ui.dialog.run()
        self.ui.dialog.hide()

    def destroy(self):
        """Destroy the About dialog"""
        logging.debug(f'{self.__class__.__name__} destroy')
        self.ui.dialog.destroy()
