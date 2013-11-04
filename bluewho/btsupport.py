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
    major_classes = (
      (BT_DEVICETYPE_UNKNOWN, _('unknown')),
      (BT_DEVICETYPE_COMPUTER, _('computer')),
      (BT_DEVICETYPE_PHONE, _('phone')),
      (BT_DEVICETYPE_NETWORK, _('network')),
      (BT_DEVICETYPE_AUDIOVIDEO, _('audio-video')),
      (BT_DEVICETYPE_PERIPHERAL, _('peripheral')),
      (BT_DEVICETYPE_IMAGING, _('imaging')),
      (BT_DEVICETYPE_UNCATEGORIZED, _('uncategorized'))
    )
    if major_class >= len(major_classes):
      major_class = BT_DEVICETYPE_UNKNOWN        # Fallback to unknown class
    return major_classes[major_class]

  def get_device_detail(self, major_class, minor_class):
    "Return the device detail type"
    uncategorized = _('uncategorized')
      
    if major_class == BT_DEVICETYPE_MISCELLANEOUS:
      return (0, uncategorized)
    if major_class == BT_DEVICETYPE_COMPUTER:
      return {
        1: (1, _('desktop workstation')),
        2: (2, _('server')),
        3: (3, _('laptop')),
        4: (4, _('handheld')),
        5: (5, _('palm')),
        6: (6, _('wearable computer'))
      }.get(minor_class, (0, uncategorized))
    elif major_class == BT_DEVICETYPE_PHONE:
      return {
        1: (1, _('cellular')),
        2: (2, _('cordless')),
        3: (3, _('smartphone')),
        4: (4, _('wired modem - voice gateway')),
        5: (5, _('common ISDN access'))
      }.get(minor_class, (0, uncategorized))
    elif major_class == BT_DEVICETYPE_NETWORK:
      return {
        0: (0, _('network fully available')),
        1: (1, _('network 1-17%% used')),
        2: (2, _('network 17-33%% used')),
        3: (3, _('network 33-50%% used')),
        4: (4, _('network 50-67%% used')),
        5: (5, _('network 67-83%% used')),
        6: (6, _('network 83-99%% used')),
        7: (7, _('network unavailable'))
      }.get(minor_class >> 3, (0, uncategorized))  # 3 lowers bit unused
    elif major_class == BT_DEVICETYPE_AUDIOVIDEO:
      return {
        1: (1, _('headset')),
        2: (2, _('hands-free')),
        4: (4, _('microphone')),
        5: (5, _('loudspeaker')),
        6: (6, _('headphone')),
        7: (7, _('portable audio')),
        8: (8, _('car audio')),
        9: (9, _('set-top box')),
        10: (10, _('hifi audio')),
        11: (11, _('vcr')),
        12: (12, _('videocamera')),
        13: (13, _('camcorder')),
        14: (14, _('video monitor')),
        15: (15, _('video display loudspeaker')),
        16: (16, _('video conferencing')),
        18: (18, _('gaming toy'))
      }.get(minor_class, (0, uncategorized))
    elif major_class == BT_DEVICETYPE_PERIPHERAL:
      if minor_class <= 15:                   # Lower 4 bits
        return {
          1: (1, _('joystick')),
          2: (1, _('gamepad')),
          3: (1, _('remote control')),
          4: (1, _('sensing device')),
          5: (1, _('digitizer tablet')),
          6: (1, _('card reader'))
        }.get(minor_class, (0, uncategorized))
      else:                                   # Higher 2 bits
        return {
          1: (81, _('keyboard')),
          2: (82, _('mouse')),
          3: (83, _('keyboard+mouse'))
        }.get(minor_class >> 4, (0, uncategorized))
    elif major_class == BT_DEVICETYPE_IMAGING:
      return {
        1: _('display'),
        2: _('camera'),
        4: _('scanner'),
        8: _('printer')
      }.get(minor_class, (0, uncategorized))
