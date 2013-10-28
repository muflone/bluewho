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

import bluetooth
from gettext import gettext as _

DEVICETYPE_MISCELLANEOUS, DEVICETYPE_COMPUTER, DEVICETYPE_PHONE, \
DEVICETYPE_NETWORK, DEVICETYPE_AUDIOVIDEO, DEVICETYPE_PERIPHERAL, \
DEVICETYPE_IMAGING, DEVICETYPE_UNCATEGORIZED, DEVICETYPE_UNKNOWN = range(9)

def getClasses(device_class):
  "Return device minor, major class and services class"
  minor_class = (device_class & 0xff) >> 2  # Bits 02-07 Minor class bitwise
  major_class = (device_class >> 8) & 0x1f  # Bits 08-12 Major class bitwise
  services_class = (device_class >> 16)     # Bits 16-23 Service class
  return (minor_class, major_class, services_class)

def getEnabledServices(service_class):
  "Return enabled services for a service_class"
  availableServices = (
    _('positioning service'),
    _('networking service'),
    _('rendering service'),
    _('capturing service'),
    _('object transfer service'),
    _('audio service'),
    _('telephony service'),
    _('information service')
  )
  services = []
  for service in range(len(availableServices)):
    if service_class & (1 << service):      # Service enabled?
      services.append(availableServices[service])
  return services

def getDeviceType(major_class):
  "Return the device major class"
  major_classes = (
    (0, _('miscellaneous')),
    (1, _('computer')),
    (2, _('phone')),
    (3, _('network')),
    (4, _('audio-video')),
    (5, _('peripheral')),
    (6, _('imaging')),
    (7, _('uncategorized'))
  )
  if major_class > DEVICETYPE_UNCATEGORIZED:
    major_class = DEVICETYPE_UNKNOWN        # Unknown class
  return major_classes[major_class]

def getDeviceDetail(major_class, minor_class):
  "Return the device detail type"
  uncategorized = _('uncategorized')
    
  if major_class == DEVICETYPE_MISCELLANEOUS:
    return (0, uncategorized)
  if major_class == DEVICETYPE_COMPUTER:
    return {
      1: (1, _('desktop workstation')),
      2: (2, _('server')),
      3: (3, _('laptop')),
      4: (4, _('handheld')),
      5: (5, _('palm')),
      6: (6, _('wearable computer'))
    }.get(minor_class, (0, uncategorized))
  elif major_class == DEVICETYPE_PHONE:
    return {
      1: (1, _('cellular')),
      2: (2, _('cordless')),
      3: (3, _('smartphone')),
      4: (4, _('wired modem - voice gateway')),
      5: (5, _('common ISDN access'))
    }.get(minor_class, (0, uncategorized))
  elif major_class == DEVICETYPE_NETWORK:
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
  elif major_class == DEVICETYPE_AUDIOVIDEO:
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
  elif major_class == DEVICETYPE_PERIPHERAL:
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
  elif major_class == DEVICETYPE_IMAGING:
    return {
      1: _('display'),
      2: _('camera'),
      4: _('scanner'),
      8: _('printer')
    }.get(minor_class, (0, uncategorized))

def get_localAdapter(deviceNr):
  "Return name and address of a local adapter"
  import struct
  from bluetooth import _bluetooth as bt

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

def listServices(address):
  "Return the list of enabled services"
  services = []
  for service in bluetooth.find_service(address=address):
    services.append((service['name'], service['protocol'], service['port']))
  return services

def getDeviceName(address):
  "Retrieve device name"
  return bluetooth.lookup_name(address)

class DeviceDiscoverer(bluetooth.DeviceDiscoverer):
  "Support for asynchron detection"
  def __init__(self):
    "Superclass constructor"
    bluetooth.DeviceDiscoverer.__init__(self)
    # Callback function to receive new discovered device
    self.newDevice = None
    
  def pre_inquiry(self):
    "Scan is starting"
    self.done = False

  def device_discovered(self, address, device_class, name):
    "Call callback function for new discovered device"
    if self.newDevice:
      self.newDevice(name, address, device_class)

  def inquiry_complete(self):
    "Scan completed"
    self.done = True
