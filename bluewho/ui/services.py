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

from gi.repository import Gtk

from bluewho.constants import FILE_ICON
from bluewho.functions import _, get_ui_file
from bluewho.ui.gtk_builder_loader import GtkBuilderLoader
from bluewho.ui.model_services import ModelServices


class DialogServices(object):
    def __init__(self, parent, show=False):
        # Load the user interface
        self.ui = GtkBuilderLoader(get_ui_file('services.glade'))
        # Obtain widget references
        dialog = self.ui.dialog
        self.model = ModelServices(self.ui.model_services)
        # Set various properties
        dialog.set_title(_('Available services'))
        dialog.set_icon_from_file(FILE_ICON)
        dialog.set_transient_for(parent)
        dialog.add_button(Gtk.STOCK_OK, Gtk.ResponseType.OK)
        dialog.set_default_response(Gtk.ResponseType.OK)
        # Optionally show the dialog
        if show:
            self.show()

    def show(self):
        """Show the Services dialog"""
        self.ui.dialog.run()
        self.ui.dialog.hide()

    def destroy(self):
        """Destroy the Services dialog"""
        self.ui.dialog.destroy()
