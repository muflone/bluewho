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

from gettext import gettext, dgettext
import os.path
import threading
from time import localtime

from gi.repository import Gtk
from gi.repository.GLib import idle_add

from bluewho.constants import DIR_UI

localized_messages = {}


def get_current_thread_ident(func):
    """Decorator function to print the active running thread"""
    def callback(*args):
        print('%s is called from %s thread' % (
            func,
            threading.current_thread().name))
        return func(*args)
    return callback


def get_current_time():
    """Returns the formatted current date and time"""
    current_time = localtime()
    return _('%(year)04d/%(month)02d/%(day)02d '
             '%(hour)02d:%(minute)02d.%(second)02d') % {
                 'day': current_time.tm_mday,
                 'month': current_time.tm_mon,
                 'year': current_time.tm_year,
                 'hour': current_time.tm_hour,
                 'minute': current_time.tm_min,
                 'second': current_time.tm_sec}


def get_ui_file(filename):
    """Return the full path of a Glade/UI file"""
    return os.path.join(DIR_UI, filename)


def process_events():
    """Let the main GTK+ loop to continue"""
    while Gtk.events_pending():
        Gtk.main_iteration()


def readlines(filename, empty_lines=False):
    """Read all lines from a text file"""
    result = []
    with open(filename) as file:
        for line in file.readlines():
            line = line.strip()
            if line or empty_lines:
                result.append(line)
    return result


def text(message, gtk30=False, context=None):
    """Return a translated message and cache it for reuse"""
    if message not in localized_messages:
        if gtk30:
            # Get a message translated from GTK+ 3 domain
            full_message = message if not context else f'{context}\04{message}'
            localized_messages[message] = dgettext('gtk30', full_message)
            # Fix for untranslated messages with context
            if context and localized_messages[message] == full_message:
                localized_messages[message] = dgettext('gtk30', message)
        else:
            localized_messages[message] = gettext(message)
    return localized_messages[message]


def text_gtk30(message, context=None):
    """Return a translated text from GTK+ 3.0"""
    return text(message=message, gtk30=True, context=context)


def thread_safe(func):
    """Decorator function to make a thread safe call to a GTK+ function"""
    def callback(*args):
        idle_add(func, *args)
    return callback


# This special alias is used to track localization requests to catch
# by xgettext. The text() calls aren't tracked by xgettext
_ = text
