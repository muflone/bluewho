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
from bluewho.functions import get_ui_file, readlines
from bluewho.ui.gtk_builder_loader import GtkBuilderLoader


class DialogAbout(object):
    def __init__(self, parent, show=False):
        # Retrieve the translators list
        translators = []
        for line in readlines(FILE_TRANSLATORS, False):
            if ':' in line:
                line = line.split(':', 1)[1]
            line = line.replace('(at)', '@').strip()
            if line not in translators:
                translators.append(line)
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('about.glade'))
        # Obtain widget references
        dialog = self.ui.dialog
        # Set various properties
        dialog.set_program_name(APP_NAME)
        dialog.set_version('Version %s' % APP_VERSION)
        dialog.set_comments(APP_DESCRIPTION)
        dialog.set_website(APP_URL)
        dialog.set_copyright(APP_COPYRIGHT)
        dialog.set_authors(['%s <%s>' % (APP_AUTHOR, APP_AUTHOR_EMAIL)])
        dialog.set_license('\n'.join(readlines(FILE_LICENSE, True)))
        dialog.set_translator_credits('\n'.join(translators))
        # Retrieve the external resources links
        for line in readlines(FILE_RESOURCES, False):
            resource_type, resource_url = line.split(':', 1)
            dialog.add_credit_section(resource_type, (resource_url,))
        icon_logo = Pixbuf.new_from_file(FILE_ICON)
        dialog.set_logo(icon_logo)
        dialog.set_transient_for(parent)
        # Optionally show the dialog
        if show:
            self.show()

    def show(self):
        """Show the About dialog"""
        self.ui.dialog.run()
        self.ui.dialog.hide()

    def destroy(self):
        """Destroy the About dialog"""
        self.ui.dialog.destroy()
