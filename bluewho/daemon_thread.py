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

from gi.repository import Gdk
from gi.repository import GObject
from threading import Thread
from threading import Event

class DaemonThread(Thread):
  def __init__(self, target, name):
    GObject.threads_init()
    Gdk.threads_init()
    super(self.__class__, self).__init__(target=target)
    self.name = name
    self.daemon = True
    self.cancelled = False
    self.paused = False
    self.event = Event()

  def cancel(self):
    self.cancelled = True

  def pause(self):
    self.paused = True

  def unpause(self):
    self.paused = False
    print 'unpausing'
    self.event.set()
