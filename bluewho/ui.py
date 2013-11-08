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
from gi.repository import Gtk
from gi.repository import Gio
from bluewho.constants import *
from bluewho.functions import *
from bluewho.settings import Settings
from bluewho.model_devices import ModelDevices
from bluewho.about import AboutWindow
from bluewho.services import ServicesDialog
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
    # Restore the devices list
    for device in self.settings.load_devices():
      self.add_device(
        device['address'],
        device['name'],
        device['class'],
        device['lastseen'],
        False)
    # Load the others dialogs
    self.about = AboutWindow(self.winMain, False)
    # Set other properties
    self.btsupport.set_new_device_cb(self.on_new_device_cb)
    self.thread_scanner = None

  def run(self):
    "Show the UI"
    self.winMain.show_all()

  def loadUI(self):
    "Load the interface UI"
    builder = Gtk.Builder()
    builder.add_from_file(FILE_UI_MAIN)
    # Obtain widget references
    self.winMain = builder.get_object("winMain")
    self.model = ModelDevices(
      builder.get_object('modelDevices'),
      self.settings,
      self.btsupport)
    self.tvwDevices = builder.get_object('tvwDevices')
    self.toolbDetect = builder.get_object('toolbDetect')
    self.statusScan = builder.get_object('statusScan')
    self.statusScanContextId = self.statusScan.get_context_id(DOMAIN_NAME)
    self.spinnerScan = builder.get_object('spinnerScan')
    # Set various properties
    self.winMain.set_title(APP_NAME)
    self.winMain.set_icon_from_file(FILE_ICON)
    self.winMain.set_application(self.application)
    # Connect signals from the glade file to the functions with the same name
    builder.connect_signals(self)

  def on_winMain_delete_event(self, widget, event):
    "Close the application"
    if self.thread_scanner:
      # Cancel the running thread
      if self.thread_scanner.isAlive():
        # Hide immediately the window and let the GTK+ cycle to continue giving
        # the perception that the app was really closed
        self.winMain.hide()
        GtkProcessEvents()
        print 'please wait for scan to complete...'
        self.thread_scanner.cancel()
        self.thread_scanner.join()
    self.thread_scanner = None
    self.about.destroy()
    self.settings.set_sizes(self.winMain)
    self.settings.save_devices(self.model)
    self.settings.save()
    self.winMain.destroy()
    self.application.quit()

  def on_toolbAbout_clicked(self, widget):
    "Show the about dialog"
    self.about.show()

  def on_toolbDetect_toggled(self, widget):
    "Reload the list of local and detected devices"
    # Start the scanner thread
    if self.toolbDetect.get_active():
      self.spinnerScan.set_visible(True)
      self.spinnerScan.start()
      assert not self.thread_scanner
      self.thread_scanner = DaemonThread(self.do_scan, 'BTScanner')
      self.set_status_bar_message('Start new scan')
      self.thread_scanner.start()
    else:
      if self.thread_scanner:
        self.toolbDetect.set_sensitive(False)
        # Check if the scanner is still running and cancel it
        if self.thread_scanner.is_alive():
          self.thread_scanner.cancel()
          self.set_status_bar_message('Cancel running scan')
        else:
          # The scanner thread has died for some error, we need to recover
          # the UI to allow the user to launch the scanner again
          print 'the thread has died, recovering the UI'
          self.set_status_bar_message('The scanning thread has died, recovering the UI')
          self.spinnerScan.stop()
          self.spinnerScan.set_visible(False)
          self.thread_scanner = None
          self.toolbDetect.set_sensitive(True)

  @thread_safe
  def on_toolbClear_clicked(self, widget):
    "Clear the devices list"
    self.model.clear()
    #foundDevices.clear()

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
      self.add_device(
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

  @thread_safe
  def add_device(self, address, name, device_class, time, notify):
    self.set_status_bar_message('Found new device %s [%s]' % (name, address))
    self.model.add_device(address, name, device_class, time, notify)
    return False

  @get_current_thread_ident
  def do_scan(self):
    from random import randint
    while True:
    #if True:
      # Cancel the running thread
      if self.thread_scanner.cancelled:
        break
      # Wait until an event awakes the thread again
      if self.thread_scanner.paused:
        print self.thread_scanner.event.wait()
        self.thread_scanner.event.clear()
      # Add local adapters
      for devices_count in range(10):
        name, address = self.btsupport.get_localAdapter(devices_count)
        if name and address:
          # Adapter device found
          #if not foundDevices.get(address):
          #if settings.get('show local'):
          name = 'hci%d (%s)' % (devices_count, name)
          if True:
            self.add_device(address, name, 0, get_current_time(), True)
              #modelRow = modelDevices[-1]
              #foundDevices[address] = modelRow
              # Update seen time
              #modelRow[COL_LASTSEEN] = getCurrentTime()
        else:
          # No more devices found
          if devices_count==0:
            print 'error: no local devices found, unable to continue'
            #idle_add(GtkMessageDialogOK,
            #  self.winMain, 
            #  _('No local devices found during detection.'),
            #  Gtk.MessageType.WARNING)
            GtkMessageDialogOK(self.winMain, _('No local devices found during detection.'), Gtk.MessageType.WARNING, False)
            self.set_status_bar_message(_('No local devices found during detection.'))
            # Disable autoscan
            self.thread_scanner = None
            idle_add(self.spinnerScan.stop)
            idle_add(self.spinnerScan.set_visible, False)
            idle_add(self.toolbDetect.set_active, False)
            return True
          break

      # What is this? useful for testing purposes, you can just ignore it
      if randint(0, 1) == 1:
        self.on_new_device_cb('TEST 1', '00:11:22:33:44:55', 5211141)
      if randint(0, 1) == 1:
        self.on_new_device_cb('TEST 2', '88:77:66:55:44:33', 1704212)
      if randint(0, 1) == 1:
        self.on_new_device_cb('TEST 3', '55:44:33:22:11:00', 7864836)

      self.btsupport.discover()

    self.thread_scanner = None
    self.set_status_bar_message(None)
    idle_add(self.spinnerScan.stop)
    idle_add(self.spinnerScan.set_visible, False)
    idle_add(self.toolbDetect.set_sensitive, True)
    return False

  def on_toolbServices_clicked(self, widget):
    "Show the available services dialog for the selected device"
    selected = self.tvwDevices.get_selection().get_selected()[1]
    if selected:
      # Get the device address
      address = self.model.get_type(selected) == 'adapter' and \
        'localhost' or self.model.get_address(selected)
      # Show the services dialog
      dialog = ServicesDialog(self.winMain, False)
      # Load the list of enabled services
      for service in self.btsupport.get_services(address):
        dialog.model.add_service(service)
      dialog.show()

  @thread_safe
  def set_status_bar_message(self, message=None):
    self.statusScan.pop(self.statusScanContextId)
    if message is not None:
      self.statusScan.push(self.statusScanContextId, message)
