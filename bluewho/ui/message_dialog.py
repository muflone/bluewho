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


class MessageDialog(Gtk.Window):
    def __init__(self, parent, message_type, title, msg1, msg2,
                 buttons, default_response_id):
        """Prepare the message dialog"""
        self.dialog = Gtk.MessageDialog(parent=parent,
                                        flags=Gtk.DialogFlags.MODAL,
                                        message_type=message_type,
                                        buttons=buttons,
                                        title=title,
                                        message_format=msg1,
                                        secondary_text=msg2)
        if default_response_id:
            self.dialog.set_default_response(default_response_id)

    def run(self):
        """Show the dialog"""
        result = self.dialog.run()
        self.dialog.hide()
        self.destroy()
        return result

    def destroy(self):
        """Destroy the dialog"""
        self.dialog.destroy()
        self.dialog = None


class MessageDialogOK(MessageDialog):
    def __init__(self, parent, message_type, title, msg1, msg2):
        """Prepare the message dialog with an OK button"""
        MessageDialog.__init__(self,
                               parent=parent,
                               message_type=message_type,
                               title=title,
                               msg1=msg1,
                               msg2=msg2,
                               buttons=Gtk.ButtonsType.OK,
                               default_response_id=Gtk.ResponseType.OK)


class MessageDialogOKCancel(MessageDialog):
    def __init__(self, parent, message_type, title, msg1, msg2):
        """Prepare the message dialog with OK and Cancel buttons"""
        MessageDialog.__init__(self,
                               parent=parent,
                               message_type=message_type,
                               title=title,
                               msg1=msg1,
                               msg2=msg2,
                               buttons=Gtk.ButtonsType.OK_CANCEL,
                               default_response_id=Gtk.ResponseType.OK)


class MessageDialogCancelOK(MessageDialog):
    def __init__(self, parent, message_type, title, msg1, msg2):
        """Prepare the message dialog with Cancel and OK buttons"""
        MessageDialog.__init__(self,
                               parent=parent,
                               message_type=message_type,
                               title=title,
                               msg1=msg1,
                               msg2=msg2,
                               buttons=Gtk.ButtonsType.OK_CANCEL,
                               default_response_id=Gtk.ResponseType.CANCEL)


class MessageDialogClose(MessageDialog):
    def __init__(self, parent, message_type, title, msg1, msg2):
        """Prepare the message dialog with a Close button"""
        MessageDialog.__init__(self,
                               parent=parent,
                               message_type=message_type,
                               title=title,
                               msg1=msg1,
                               msg2=msg2,
                               buttons=Gtk.ButtonsType.CLOSE,
                               default_response_id=Gtk.ResponseType.CLOSE)


class MessageDialogYesNo(MessageDialog):
    def __init__(self, parent, message_type, title, msg1, msg2):
        """Prepare the message dialog with Yes and No buttons"""
        MessageDialog.__init__(self,
                               parent=parent,
                               message_type=message_type,
                               title=title,
                               msg1=msg1,
                               msg2=msg2,
                               buttons=Gtk.ButtonsType.YES_NO,
                               default_response_id=Gtk.ResponseType.YES)


class MessageDialogNoYes(MessageDialog):
    def __init__(self, parent, message_type, title, msg1, msg2):
        """Prepare the message dialog with No and Yes buttons"""
        MessageDialog.__init__(self,
                               parent=parent,
                               message_type=message_type,
                               title=title,
                               msg1=msg1,
                               msg2=msg2,
                               buttons=Gtk.ButtonsType.YES_NO,
                               default_response_id=Gtk.ResponseType.NO)
