#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import gtk
import gtk.glade
import pygtk
import sys
import os.path
import select
import btsupport
import settings
import subprocess
import time
import gettext
import handlepaths
from gettext import gettext as _

foundDevices = {}
statusBarContextId = 0

def playSound():
  "Play sound for detected devices"
  proc = subprocess.Popen(['aplay', '-q', settings.get('sound file')], 
    stdout=subprocess.PIPE)

def readTextFile(filename):
  "Read a text file and return its content"
  try:
    f = open(filename, 'r')
    text = f.read()
    f.close()
  except:
    text = ''
  return text

def addNewDevice(address, name, deviceClass, time, notify):
  "Add a new device to the list and pops notification"
  if deviceClass > 0:
    minor_class, major_class, services_class = btsupport.getClasses(deviceClass)
    deviceType = btsupport.getDeviceType(major_class)
    deviceDetail = btsupport.getDeviceDetail(major_class, minor_class)
  else:
    deviceType = (0, 'adapter')
    deviceDetail = (0, _('adapter'))
  iconPath = getIconPath(deviceType[0], deviceDetail[0])

  modelDevices.append([
    gtk.gdk.pixbuf_new_from_file(iconPath),
    deviceClass, deviceType[1], deviceDetail[1], name, address, time
  ])
  if notify:
    if settings.get('play sound'):
      playSound()
    if settings.get('show notification'):
      command = settings.get('notify cmd').replace('\\n', '\n') % {
        'icon': iconPath, 'name': name and name or '', 'address': address }
      proc = subprocess.Popen(command, shell=True)
      proc.communicate()

def getCurrentTime():
  "Returns the formatted current date and time"
  currentTime = time.localtime()
  return _('%(year)04d/%(month)02d/%(day)02d ' \
    '%(hour)02d:%(minute)02d.%(second)02d') % {
    'day': currentTime.tm_mday,
    'month': currentTime.tm_mon,
    'year': currentTime.tm_year,
    'hour': currentTime.tm_hour,
    'minute': currentTime.tm_min,
    'second': currentTime.tm_sec
  }
  
def executeScan():
  "Scan for local and remote devices"
  # Add local adapters
  if settings.get('show local'):
    for i in range(10):
      name, address = btsupport.get_localAdapter(i)
      if name and address:
        # Adapter device found
        if not foundDevices.get(address):
          name = 'hci%d (%s)' % (i, name)
          addNewDevice(address, name, 0, getCurrentTime(), True)
          modelRow = modelDevices[-1]
          foundDevices[address] = modelRow
          # Update seen time
          modelRow[COL_LASTSEEN] = getCurrentTime()
      else:
        # No more devices found
        if i==0:
          print 'error: no local devices found, unable to continue'
          diag = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, 
            gtk.BUTTONS_OK, _('No local devices found during detection.'))
          diag.set_icon_from_file(handlepaths.get_app_logo())
          diag.run()
          diag.destroy()
          # Disable autoscan
          toolbAutoScan.set_active(False)
          return
        break
    
  # Add detected devices
  devices = btsupport.DeviceDiscoverer()
  devices.newDevice = on_newDevice
  try:
    devices.find_devices(
      lookup_names=settings.get('retrieve names'),
      duration=settings.get('scan duration'),
      flush_cache=settings.get('flush cache')
    )
  except:
    devices.done = True
    toolbAutoScan.set_active(False)
  readfiles = [ devices, ]
  # Wait till the end
  while not devices.done:
    progSearching.pulse()
    while gtk.events_pending():
      gtk.main_iteration()
    ret = select.select( readfiles, [], [] )[0]
    if devices in ret:
      devices.process_event()
  lastscan = time.localtime()
  statusScan.pop(statusBarContextId)
  statusScan.push(statusBarContextId, _('Last scan: %s') % getCurrentTime())

def createDevicesColumns():
  "Create columns for devices list"
  # Column for device icon
  cell = gtk.CellRendererPixbuf()
  column = gtk.TreeViewColumn('')
  column.pack_start(cell)
  column.set_attributes(cell, pixbuf=COL_ICON)
  tvwDevices.append_column(column)

  # Column for device type
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Type'))
  column.pack_start(cell)
  column.set_expand(True)
  column.set_attributes(cell, text=COL_DETAIL)
  tvwDevices.append_column(column)

  # Column for device name
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Device name'))
  column.pack_start(cell)
  column.set_expand(True)
  column.set_attributes(cell, text=COL_NAME)
  tvwDevices.append_column(column)

  # Column for device address
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Bluetooth address'))
  column.pack_start(cell)
  column.set_attributes(cell, text=COL_ADDRESS)
  tvwDevices.append_column(column)

  # Column for device address
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Last seen'))
  column.pack_start(cell)
  column.set_attributes(cell, text=COL_LASTSEEN)
  tvwDevices.append_column(column)

def createServicesColumns():
  "Create columns for services list"
  # Column for service name
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Service name'))
  column.pack_start(cell)
  column.set_attributes(cell, text=0)
  tvwServices.append_column(column)

  # Column for service protocol
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Protocol'))
  column.pack_start(cell)
  column.set_attributes(cell, text=1)
  tvwServices.append_column(column)

  # Column for service channel
  cell = gtk.CellRendererText()
  column = gtk.TreeViewColumn(_('Channel'))
  column.pack_start(cell)
  column.set_attributes(cell, text=2)
  tvwServices.append_column(column)

def saveDevicesList(filename):
  "Save devices list to filename"
  saveFile = open(filename, 'w')
  for device in modelDevices:
    saveFile.write('%s\n%s\n%d\n%s\n>\n' % (
      device[COL_ADDRESS], device[COL_NAME],
      device[COL_CLASS], device[COL_LASTSEEN]))
  saveFile.close()

def loadDevicesList(filename):
  "Load devices list from filename"
  loadFile = open(filename, 'r')
  devices = loadFile.read().split('\n>\n')
  for device in devices:
    if len(device) > 0:
      device = device.split('\n')
      addNewDevice(device[0], device[1], int(device[2]), device[3], False)
      foundDevices[device[0]] = modelDevices[-1]
  loadFile.close()

def getIconPath(deviceType, deviceDetail):
  "Return the icon path for a device"
  if deviceType == 0 and deviceDetail == 0:
    # Adapter
    iconPath = handlepaths.getPath('gfx', 'adapter.png')
  else:
    # Normal device
    iconPath = handlepaths.getPath('gfx', 'class%d/%d.png' % (
      deviceType, deviceDetail))
    if not os.path.isfile(iconPath):
      iconPath = handlepaths.getPath('gfx', 'unknown.png')
  return os.path.join(handlepaths.base_path, iconPath)

def on_newDevice(name, address, device_class):
  "Callback function called when a new device has been discovered"
  modelRow = foundDevices.get(address)
  # Search for the name if not found during scan
  if not name and settings.get('resolve names'):
    # Search name if the device exists without name or if doesn't exist at all
    if (modelRow and not modelRow[COL_NAME]) or not modelRow:
      # Find name by scanning device
      name = btsupport.getDeviceName(address)
  if name is None:
    name = ''
  # If device doesn't exist then add it
  if not modelRow:
    addNewDevice(address, name, device_class, 
      getCurrentTime(), True)
    modelRow = modelDevices[-1]
    foundDevices[address] = modelRow
  else:
    # Sets the new name if it didn't exist
    if not modelRow[COL_NAME] and name:
      modelRow[COL_NAME] = name
    # Update seen time
    modelRow[COL_LASTSEEN] = getCurrentTime()

def on_winDevices_delete_event(widget, data=None):
  "Close the main Window and gtk main loop"
  dialogServices.destroy()
  gtk.main_quit()
  cursize = winDevices.get_size()
  curpos = winDevices.get_position()
  saveDevicesList(settings.devicesfiles)
  settings.set('window width', cursize[0])
  settings.set('window height', cursize[1])
  settings.set('window left', curpos[0])
  settings.set('window top', curpos[1])
  return 0

def on_toolbRefresh_clicked(widget, data=None):
  "Reload the list of local and detected devices"
  progSearching.show()
  toolbRefresh.set_sensitive(False)
  toolbServices.set_sensitive(False)
  # Single scan
  executeScan()
  # Automatic scan
  while toolbAutoScan.get_active():
    while gtk.events_pending():
      gtk.main_iteration()
    executeScan()
  #
  # What is this? useful for testing purposes, you can just ignore it
  # on_newDevice('STEFANIA', '00:11:22:33:44:55', 5211141)
  #
  # Hide pulsing progressbar
  progSearching.hide()
  toolbRefresh.set_sensitive(True)

def on_toolbServices_clicked(widget, data=None):
  "Show the details of the selected device"
  iter = modelDevices[tvwDevices.get_selection().get_selected()[1]]
  modelServices.clear()
  address = iter[COL_TYPE] == 'adapter' and 'localhost' or iter[COL_ADDRESS]
  # Load the list of enabled services
  services = btsupport.listServices(address)
  for service in services:
    modelServices.append([service[0], service[1], service[2]])
  dialogServices.run()
  dialogServices.hide()

def on_toolbClear_clicked(widget, data=None):
  "Clear the devices list"
  modelDevices.clear()
  foundDevices.clear()
  toolbServices.set_sensitive(False)

def on_toolbPreferences_clicked(widget, data=None):
  "Show preferences and save settings"
  dialogPreferences.run()
  dialogPreferences.hide()
  settings.set('startup scan', chkStartupScan.get_active())
  settings.set('autoscan', chkAutoScan.get_active())
  settings.set('retrieve names', chkRetrieveName.get_active())
  settings.set('resolve names', chkResolveNames.get_active())
  settings.set('show local', chkLocalAdapters.get_active())
  settings.set('notify cmd', txtNotificationCmd.get_text())
  settings.set('show notification', chkNotification.get_active())
  settings.set('play sound', chkPlaySound.get_active())
  settings.set('sound file', filePlaySound.get_filename())
  settings.save(clearDefaults=True)

def on_toolbAbout_clicked(widget, data=None):
  "Shows the about dialog"
  about = gtk.AboutDialog()
  about.set_program_name(handlepaths.APP_TITLE)
  about.set_version(handlepaths.APP_VERSION)
  about.set_comments(_('A GTK utility to inform and notify you when a new '
    'bluetooth device is discovered.'))
  about.set_icon_from_file(handlepaths.get_app_logo())
  about.set_logo(gtk.gdk.pixbuf_new_from_file(handlepaths.get_app_logo()))
  about.set_copyright('Copyright 2009 Fabio Castelli')
  about.set_translator_credits(readTextFile(handlepaths.getPath('doc','translators')))
  about.set_license(readTextFile(handlepaths.getPath('doc','copyright')))
  about.set_website_label('BlueWho')
  gtk.about_dialog_set_url_hook(lambda url, data=None: url)
  about.set_website('http://code.google.com/p/bluewho/')
  about.set_authors(['Fabio Castelli <muflone@vbsimple.net>', 
    'http://www.ubuntutrucchi.it'])
  about.run()
  about.destroy()

def on_tvwDevices_cursor_changed(widget, data=None):
  "Control sensitiveness of the buttons"
  if tvwDevices.get_selection().get_selected()[1]:
    toolbServices.set_sensitive(True)

def on_btnPlay_clicked(widget, data=None):
  playSound()

# Signals handler
signals = {
  'on_winDevices_delete_event': on_winDevices_delete_event,
  'on_toolbRefresh_clicked': on_toolbRefresh_clicked,
  'on_toolbClear_clicked': on_toolbClear_clicked,
  'on_toolbServices_clicked': on_toolbServices_clicked,
  'on_toolbPreferences_clicked': on_toolbPreferences_clicked,
  'on_toolbAbout_clicked': on_toolbAbout_clicked,
  'on_tvwDevices_cursor_changed': on_tvwDevices_cursor_changed,
  'on_btnPlay_clicked': on_btnPlay_clicked
}

# Load domain for translation
for module in (gettext, gtk.glade):
  module.bindtextdomain(handlepaths.APP_NAME, handlepaths.getPath('locale'))
  module.textdomain(handlepaths.APP_NAME)

gladeFile = gtk.glade.XML(
  fname=handlepaths.getPath('data', '%s.glade' % handlepaths.APP_NAME),
  domain=handlepaths.APP_NAME)
gladeFile.signal_autoconnect(signals)
gw = gladeFile.get_widget
# Main window
winDevices = gw('winDevices')
winDevices.set_icon_from_file(handlepaths.get_app_logo())
winDevices.set_title(handlepaths.APP_TITLE)
tvwDevices = gw('tvwDevices')
toolbRefresh = gw('toolbRefresh')
toolbAutoScan = gw('toolbAutoScan')
toolbServices = gw('toolbServices')
progSearching = gw('progSearching')
statusScan = gw('statusScan')
statusBarContextId = statusScan.get_context_id(handlepaths.APP_NAME)
# Model for devices (icon, class, type, detail, name, mac, last seen)
modelDevices = gtk.ListStore(gtk.gdk.Pixbuf, int, str, str, str, str, str)
COL_ICON, COL_CLASS, COL_TYPE, COL_DETAIL, \
  COL_NAME, COL_ADDRESS, COL_LASTSEEN = range(7)
tvwDevices.set_model(modelDevices)
createDevicesColumns()

# Properties window
dialogServices = gw('dialogServices')
dialogServices.set_icon_from_file(handlepaths.get_app_logo())
dialogServices.set_title(handlepaths.APP_TITLE)
tvwServices = gw('tvwServices')
# Model for services (name, protocol, port)
modelServices = gtk.ListStore(str, str, str)
tvwServices.set_model(modelServices)
createServicesColumns()

# Preferences window
dialogPreferences = gw('dialogPreferences')
dialogPreferences.set_icon_from_file(handlepaths.get_app_logo())
dialogPreferences.set_title(handlepaths.APP_TITLE)
chkStartupScan = gw('chkStartupScan')
chkAutoScan = gw('chkAutoScan')
chkRetrieveName = gw('chkRetrieveName')
chkResolveNames = gw('chkResolveNames')
chkLocalAdapters = gw('chkLocalAdapters')
txtNotificationCmd = gw('txtNotificationCmd')
chkNotification = gw('chkNotification')
chkPlaySound = gw('chkPlaySound')
filePlaySound = gw('filePlaySound')

# Load settings from ~/.config/bluewho.conf
settings.load()
winDevices.move(settings.get('window left'), settings.get('window top'))
winDevices.set_default_size(settings.get('window width'), settings.get('window height'))
chkStartupScan.set_active(settings.get('startup scan'))
chkAutoScan.set_active(settings.get('autoscan'))
chkRetrieveName.set_active(settings.get('retrieve names'))
chkResolveNames.set_active(settings.get('resolve names'))
chkLocalAdapters.set_active(settings.get('show local'))
txtNotificationCmd.set_text(settings.get('notify cmd'))
chkNotification.set_active(settings.get('show notification'))
chkPlaySound.set_active(settings.get('play sound'))
filePlaySound.set_filename(settings.get('sound file'))

# Load devices list from ~/.config/devices
if os.path.exists(settings.devicesfiles):
  loadDevicesList(settings.devicesfiles)
winDevices.show()
toolbAutoScan.set_active(settings.get('autoscan'))
if settings.get('startup scan'):
  on_toolbRefresh_clicked(None)
gtk.main()
# Save settings on close
settings.save(clearDefaults=True)
