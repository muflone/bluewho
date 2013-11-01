##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices.
#      Author: Fabio Castelli (Muflone) <webreg@vbsimple.net>
#   Copyright: 2009-2013 Fabio Castelli
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

import threading
from time import localtime
from gettext import gettext as _
from gi.repository import Gtk
from gi.repository.GObject import idle_add
from bluewho.constants import *

def thread_safe(func):
  "Decorator function to make a thread safe call to a GTK+ function"
  def callback(*args):
    idle_add(func, *args)
  return callback
    
def readlines(filename, empty_lines = False):
  "Read all lines from a text file"
  result = []
  with open(filename) as f:
    for line in f.readlines():
      line = line.strip()
      if line or empty_lines:
        result.append(line)
    f.close()
  return result

def get_current_time():
  "Returns the formatted current date and time"
  current_time = localtime()
  return _('%(year)04d/%(month)02d/%(day)02d ' \
    '%(hour)02d:%(minute)02d.%(second)02d') % {
    'day': current_time.tm_mday,
    'month': current_time.tm_mon,
    'year': current_time.tm_year,
    'hour': current_time.tm_hour,
    'minute': current_time.tm_min,
    'second': current_time.tm_sec
  }

def GtkProcessEvents():
  "Let the main GTK+ loop to continue"
  while Gtk.events_pending():
    Gtk.main_iteration()

def GtkMessageDialogOK(parent, message, type=Gtk.MessageType.INFO):
  "Show a GTK+ dialog with OK button only"
  dialog = Gtk.MessageDialog(
    parent=parent,
    flags=Gtk.DialogFlags.MODAL,
    type=type,
    buttons=Gtk.ButtonsType.OK,
    message_format=message
  )
  dialog.set_title(APP_NAME)
  dialog.set_icon_from_file(FILE_ICON)
  dialog.run()
  dialog.destroy()

def get_current_thread_ident(func):
  "Decorator function to print the active running thread"
  def callback(*args):
    print '%s is called from %s thread' % (func, threading.current_thread().name)
    return func(*args)
  return callback
  
__all__ = [
  'readlines',
  'get_current_time',
  'GtkProcessEvents',
  'GtkMessageDialogOK',
  'thread_safe',
  'idle_add',
  'get_current_thread_ident',
  '_'
]
