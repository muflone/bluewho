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

import shutil
import select
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import GObject
from bluewho.constants import *
from bluewho.functions import *
from bluewho.settings import Settings
from bluewho.model_devices import ModelDevices
from bluewho.about import AboutWindow
from bluewho.daemon_thread import DaemonThread

class MainWindow(object):
  @get_current_thread_ident
  def __init__(self, application, settings, btsupport):
    self.application = application
    self.settings = settings
    self.btsupport = btsupport
    self.is_refreshing = False
    self.loadUI()
    # Restore the saved size and position
    if self.settings.get_value('width', 0) and self.settings.get_value('height', 0):
      self.winMain.set_default_size(
        self.settings.get_value('width', -1),
        self.settings.get_value('height', -1))
    if self.settings.get_value('left', 0) and self.settings.get_value('top', 0):
      self.winMain.move(
        self.settings.get_value('left', 0),
        self.settings.get_value('top', 0))
    # Load the others dialogs
    self.about = AboutWindow(self.winMain, False)
    # Set other properties
    self.btsupport.set_new_device_cb(self.on_new_device_cb)
    self.thread_scanner = DaemonThread(self.do_scan)

  @get_current_thread_ident
  def run(self):
    "Show the UI"
    self.winMain.show_all()

  @get_current_thread_ident
  def loadUI(self):
    "Load the interface UI"
    builder = Gtk.Builder()
    builder.add_from_file(FILE_UI_MAIN)
    # Obtain widget references
    self.winMain = builder.get_object("winMain")
    self.model = ModelDevices(builder.get_object('modelDevices'), self.settings, self.btsupport)
    self.tvwResources = builder.get_object('tvwResources')
    self.toolbRefresh = builder.get_object('toolbRefresh')
    self.toolbAutoScan = builder.get_object('toolbAutoScan')
    self.toolbServices = builder.get_object('toolbServices')
    self.spinnerScan = builder.get_object('spinnerScan')
    # Set various properties
    self.winMain.set_title(APP_NAME)
    self.winMain.set_icon_from_file(FILE_ICON)
    self.winMain.set_application(self.application)
    # Connect signals from the glade file to the functions with the same name
    builder.connect_signals(self)

  @get_current_thread_ident
  def on_winMain_delete_event(self, widget, event):
    "Close the application"
    # Cancel the running thread
    if self.thread_scanner.isAlive():
      # Hide immediately the window and let the GTK+ cycle to continue giving
      # the perception that the app was really closed
      self.winMain.hide()
      GtkProcessEvents()
      print 'please wait for scan to complete...'
      self.thread_scanner.cancel()
      self.thread_scanner.join()
    self.about.destroy()
    self.settings.set_sizes(self.winMain)
    self.settings.save()
    self.winMain.destroy()
    self.application.quit()

  @get_current_thread_ident
  def on_toolbAbout_clicked(self, widget):
    "Show the about dialog"
    self.about.show()

  @get_current_thread_ident
  def on_toolbRefresh_clicked(self, widget):
    "Reload the list of local and detected devices"
    self.spinnerScan.set_visible(True)
    self.spinnerScan.start()
    self.toolbRefresh.set_sensitive(False)
    self.toolbServices.set_sensitive(False)
    # Let the interface to continue its main loop
    GtkProcessEvents()
    # Start the scanner thread
    self.thread_scanner.start()
    # Automatic scan
    #while self.toolbAutoScan.get_active():
    self.spinnerScan.stop()
    self.spinnerScan.set_visible(False)
    self.toolbRefresh.set_sensitive(True)
    print 'done'

  @get_current_thread_ident
  def on_toolbClear_clicked(self, widget):
    "Clear the devices list"
    self.model.clear()
    #foundDevices.clear()
    self.toolbServices.set_sensitive(False)

  @get_current_thread_ident
  def on_new_device_cb(self, name, address, device_class):
    "Callback function called when a new device has been discovered"
    modelRow = None
    #modelRow = foundDevices.get(address)
    # Search for the name if not found during scan
    #if not name and settings.get('resolve names'):
    if False:
      # Search name if the device exists without name or if doesn't exist at all
      if True:
      #if (modelRow and not modelRow[COL_NAME]) or not modelRow:
        # Find name by scanning device
        name = self.btsupport.get_device_name(address)
    if name is None:
      name = ''
    # If device doesn't exist then add it
    if not modelRow:
      print self.model.add_device(
        address,
        name,
        device_class,
        get_current_time(),
        True)
      #modelRow = self.model[-1]
      #foundDevices[address] = modelRow
    else:
      # Sets the new name if it didn't exist
      #if not modelRow[COL_NAME] and name:
      #  modelRow[COL_NAME] = name
      ## Update seen time
      #modelRow[COL_LASTSEEN] = getCurrentTime()
      pass

  @get_current_thread_ident
  def do_scan(self):
    # Add local adapters
    #if settings.get('show local'):
    if True:
      for i in range(10):
        name, address = self.btsupport.get_localAdapter(i)
        if name and address:
          # Adapter device found
          #if not foundDevices.get(address):
          name = 'hci%d (%s)' % (i, name)
          self.model.add_device(address, name, 0, get_current_time(), True)
            #modelRow = modelDevices[-1]
            #foundDevices[address] = modelRow
            # Update seen time
            #modelRow[COL_LASTSEEN] = getCurrentTime()
        else:
          # No more devices found
          if i==0:
            print 'error: no local devices found, unable to continue'
            GtkMessageDialogOK(self.winMain, 
              _('No local devices found during detection.'),
              Gtk.MessageType.WARNING)
            # Disable autoscan
            self.toolbAutoScan.set_active(False)
            return
          break

    from random import randint
    while True:
    #if True:
      # Cancel the running thread
      if self.thread_scanner.cancelled:
        print 'break'
        break
      else:
        print 'cycle'
      self.on_toolbClear_clicked(None)
      # What is this? useful for testing purposes, you can just ignore it
      if randint(0, 1) == 1:
        self.on_new_device_cb('TEST 1', '00:11:22:33:44:55', 5211141)
      if randint(0, 1) == 1:
        self.on_new_device_cb('TEST 2', '88:77:66:55:44:33', 1704212)
      if randint(0, 1) == 1:
        self.on_new_device_cb('TEST 3', '55:44:33:22:11:00', 7864836)

      # Add detected devices
      devices = self.btsupport.new_discoverer()
      #try:
      if True:
        devices.find_devices(
          lookup_names=True,
          duration=8,
          flush_cache=False
        )
      #else:
      #  devices.find_devices(
      #    lookup_names=settings.get('retrieve names'),
      #    duration=settings.get('scan duration'),
      #    flush_cache=settings.get('flush cache')
      #  )
      #except:
      #  devices.done = True
      #  self.toolbAutoScan.set_active(False)
      readfiles = [ devices, ]
      # Wait till the end
      while not devices.done:
        #self.progScanning.pulse()
        #GtkProcessEvents()
        ret = select.select( readfiles, [], [] )[0]
        if devices in ret:
          devices.process_event()
      #lastscan = time.localtime()
      #statusScan.pop(statusBarContextId)
      #statusScan.push(statusBarContextId, _('Last scan: %s') % getCurrentTime())
    return False
