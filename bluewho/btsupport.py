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

import struct
import select
import bluetooth
from bluetooth import _bluetooth as bt
from bluewho.bt_device_discoverer import BluetoothDeviceDiscoverer
from bluewho.constants import *
from bluewho.functions import *

class BluetoothSupport(object):
  def __init__(self):
    self.new_device_cb = None
    # Load classes from file FILE_BT_CLASSES
    self.classes = {}
    for line in readlines(FILE_BT_CLASSES):
      # Skip comments
      if '#' in line:
        line = line.split('#', 1)[0]
      # Skip empty lines
      line = line.strip()
      if line:
        # File format: Major class | Minor class | PNG Image | Description
        major_class, minor_class, image_path, description = line.split(' | ', 3)
        major_class = int(major_class)
        minor_class = int(minor_class)
        image_path = image_path.strip()
        # New major class
        if not self.classes.has_key(major_class):
          self.classes[major_class] = {}
        # Add minor class with image and description
        self.classes[major_class][minor_class] = (image_path, description)

  def set_new_device_cb(self, new_device_cb):
    "Set the new device callback for BluetoothDeviceDiscoverer"
    self.new_device_cb = new_device_cb

  def discover(self):
    # Add detected devices
    discoverer = BluetoothDeviceDiscoverer(self.new_device_cb)
    try:
    #if True:
      discoverer.find_devices(
        lookup_names=True,
        duration=8,
        flush_cache=False
      )
    #else:
    #  discoverer.find_devices(
    #    lookup_names=settings.get('retrieve names'),
    #    duration=settings.get('scan duration'),
    #    flush_cache=settings.get('flush cache')
    #  )
    except:
      discoverer.done = True
    #  self.toolbAutoScan.set_active(False)
    readfiles = [ discoverer, ]
    # Wait till the end
    while not discoverer.done:
      ret = select.select(readfiles, [], [])[0]
      if discoverer in ret:
        discoverer.process_event()
    #lastscan = time.localtime()
    #statusScan.pop(statusBarContextId)
    #statusScan.push(statusBarContextId, _('Last scan: %s') % getCurrentTime())
    pass
    
  def get_localAdapter(self, deviceNr):
    "Return name and address of a local adapter"
    name = None
    address = None
    sock = bt.hci_open_dev(deviceNr)
    if sock.getsockid() >= 0:
      sock.settimeout(3)
      # Save original filter
      orig_filter = sock.getsockopt(bt.SOL_HCI, bt.HCI_FILTER, 14)
      # Create new filter
      new_filter = orig_filter
      new_filter = bt.hci_filter_new()
      bt.hci_filter_set_ptype(new_filter, bt.HCI_EVENT_PKT)
      bt.hci_filter_set_event(new_filter, bt.EVT_CMD_COMPLETE)
      # CMD Read local name
      opcode = bt.cmd_opcode_pack(bt.OGF_HOST_CTL, bt.OCF_READ_LOCAL_NAME)
      bt.hci_filter_set_opcode(new_filter, opcode)
      sock.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, new_filter)
      bt.hci_send_cmd(sock, bt.OGF_HOST_CTL, bt.OCF_READ_LOCAL_NAME)
      try:
        data = sock.recv(255)
        name = data[7:]
        name = name[:name.find('\0')]
      except bluetooth._bluetooth.timeout:
        print 'bluetooth timeout during local device scan for name'
      # CMD Read local address
      opcode = bt.cmd_opcode_pack(bt.OGF_INFO_PARAM, bt.OCF_READ_BD_ADDR)
      bt.hci_filter_set_opcode(new_filter, opcode)
      sock.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, new_filter)
      bt.hci_send_cmd(sock, bt.OGF_INFO_PARAM, bt.OCF_READ_BD_ADDR)
      try:
        data = sock.recv(255)
        status, raw_bdaddr = struct.unpack("xxxxxxB6s", data)
        address = ['%02X' % ord(b) for b in raw_bdaddr]
        address.reverse()
        address = ':'.join(address)
      except bluetooth._bluetooth.timeout:
        print 'bluetooth timeout during local device scan for address'

      # Restore original filter
      sock.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, orig_filter)
    sock.close()
    return name, address

  def get_device_name(self, address):
    "Retrieve device name"
    return bluetooth.lookup_name(address)

  def get_classes(self, device_class):
    "Return device minor, major class and services class"
    minor_class = (device_class & 0xff) >> 2  # Bits 02-07 Minor class bitwise
    major_class = (device_class >> 8) & 0x1f  # Bits 08-12 Major class bitwise
    services_class = (device_class >> 16)     # Bits 16-23 Service class
    return (minor_class, major_class, services_class)

  def get_device_type(self, major_class):
    "Return the device major class"
    major_classes = {
      BT_DEVICETYPE_UNKNOWN: 'unknown',
      BT_DEVICETYPE_COMPUTER: 'computer',
      BT_DEVICETYPE_PHONE: 'phone',
      BT_DEVICETYPE_NETWORK: 'network',
      BT_DEVICETYPE_AUDIOVIDEO: 'audio-video',
      BT_DEVICETYPE_PERIPHERAL: 'peripheral',
      BT_DEVICETYPE_IMAGING: 'imaging',
      BT_DEVICETYPE_MISCELLANEOUS: 'miscellaneous',
      BT_DEVICETYPE_TOY: 'toy',
      BT_DEVICETYPE_HEALTH: 'health',
    }
    if not major_classes.has_key(major_class):
      major_class = BT_DEVICETYPE_UNKNOWN        # Fallback to unknown class
    return major_classes[major_class]

  def get_device_detail(self, major_class, minor_class):
    "Return the device detail type or fallback to the unknown device"
    return self.classes.get(major_class, BT_DEVICETYPE_UNKNOWN).get(
      minor_class, self.classes[BT_DEVICETYPE_UNKNOWN][0])
