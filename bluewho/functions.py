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

import datetime

from gi.repository import Gtk
from gi.repository.GLib import idle_add

from bluewho.constants import DIR_UI


def get_current_time():
    """Returns the formatted current date and time"""
    return datetime.datetime.now().strftime('%x %X')


def get_ui_file(filename):
    """Return the full path of a Glade/UI file"""
    return str(DIR_UI / filename)


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


def thread_safe(func):
    """Decorator function to make a thread safe call to a GTK+ function"""
    def callback(*args):
        idle_add(func, *args)
    return callback
