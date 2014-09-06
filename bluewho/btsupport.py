##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices.
#      Author: Fabio Castelli (Muflone) <webreg@vbsimple.net>
#   Copyright: 2009-2014 Fabio Castelli
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

# Please refer to Bluetooth specifications:
# https://www.bluetooth.org/en-us/specification/assigned-numbers
# https://www.bluetooth.org/en-us/specification/assigned-numbers/baseband

class MajorDeviceClasses(object):
  UNKNOWN = 0
  COMPUTER = 1
  PHONE = 2
  NETWORK = 3
  AUDIOVIDEO = 4
  PERIPHERAL = 5
  IMAGING = 6
  MISCELLANEOUS = 7
  TOY = 8
  HEALTH = 9
  # Dictionary for classes descriptions
  CLASSES = {
    UNKNOWN: 'unknown',
    COMPUTER: 'computer',
    PHONE: 'phone',
    NETWORK: 'network',
    AUDIOVIDEO: 'audio-video',
    PERIPHERAL: 'peripheral',
    IMAGING: 'imaging',
    MISCELLANEOUS: 'miscellaneous',
    TOY: 'toy',
    HEALTH: 'health',
  }

class ServiceDeviceClasses(object):
  POSITIONING = 1       # 0x010000 >> 16
  NETWORKING = 2        # 0x020000 >> 16
  RENDERING = 4         # 0x040000 >> 16
  CAPTURING = 8         # 0x080000 >> 16
  OBJECT_TRANSFER = 16  # 0x100000 >> 16
  AUDIO = 32            # 0x200000 >> 16
  TELEPHONY = 64        # 0x400000 >> 16
  INFORMATION = 128     # 0x800000 >> 16
  # Dictionary for services descriptions
  SERVICE_CLASSES = {
    POSITIONING: 'positioning service',
    NETWORKING: 'networking service',
    RENDERING: 'rendering service',
    CAPTURING: 'capturing service',
    OBJECT_TRANSFER: 'object transfer service',
    AUDIO: 'audio service',
    TELEPHONY: 'telephony service',
    INFORMATION: 'information service',
  }

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

  def discover(self, lookup_names, scan_duration, flush_cache):
    # Add detected devices
    discoverer = BluetoothDeviceDiscoverer(self.new_device_cb)
    try:
      discoverer.find_devices(
        lookup_names=lookup_names,
        duration=scan_duration,
        flush_cache=flush_cache
      )
    except:
      discoverer.done = True
    readfiles = [ discoverer, ]
    # Wait till the end
    while not discoverer.done:
      ret = select.select(readfiles, [], [])[0]
      if discoverer in ret:
        discoverer.process_event()
    
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
        status, raw_bdaddr = struct.unpack('xxxxxxB6s', data)
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
    if not MajorDeviceClasses.CLASSES.has_key(major_class):
      # Fallback to unknown class
      major_class = MajorDeviceClasses.UNKNOWN
    return MajorDeviceClasses.CLASSES[major_class]

  def get_device_detail(self, major_class, minor_class):
    "Return the device detail type or fallback to the unknown device"
    return self.classes.get(major_class,
      MajorDeviceClasses.UNKNOWN).get(minor_class,
      self.classes[MajorDeviceClasses.UNKNOWN][0])

  def get_services(self, address):
    "Return the list of the device's available services"
    return bluetooth.find_service(address=address)

  def get_services_from_class(self, service_class):
    "Return the enabled services for a device class"
    services = []
    for service, description in ServiceDeviceClasses.SERVICE_CLASSES.iteritems():
      if service_class & service:
        services.append(description)
    return services
