##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2009-2021 Fabio Castelli
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

import struct
import select

import bluetooth
from bluetooth import _bluetooth as bt

from bluewho.bt_device_discoverer import BluetoothDeviceDiscoverer
from bluewho.bt_major_device_classes import MajorDeviceClasses
from bluewho.bt_service_device_classes import ServiceDeviceClasses
from bluewho.constants import FILE_BT_CLASSES
from bluewho.functions import readlines


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
                # File format:
                # Major class | Minor class | PNG Image | Description
                major_class, minor_class, image_path, description = line.split(
                    ' | ', 3)
                major_class = int(major_class)
                minor_class = int(minor_class)
                image_path = image_path.strip()
                # New major class
                if major_class not in self.classes:
                    self.classes[major_class] = {}
                # Add minor class with image and description
                self.classes[major_class][minor_class] = (image_path,
                                                          description)

    def set_new_device_cb(self, new_device_cb):
        """Set the new device callback for BluetoothDeviceDiscoverer"""
        self.new_device_cb = new_device_cb

    def discover(self, lookup_names, scan_duration, flush_cache):
        # Add detected devices
        discoverer = BluetoothDeviceDiscoverer(self.new_device_cb)
        try:
            discoverer.find_devices(
              lookup_names=lookup_names,
              duration=scan_duration,
              flush_cache=flush_cache)
        except (bt.error, IndexError):
            discoverer.done = True
        readfiles = [discoverer]
        # Wait till the end
        while not discoverer.done:
            ret = select.select(readfiles, [], [])[0]
            if discoverer in ret:
                discoverer.process_event()

    def get_local_adapter(self, device_num):
        "Return name and address of a local adapter"
        name = None
        address = None
        sock = bt.hci_open_dev(device_num)
        if sock.getsockid() >= 0:
            sock.settimeout(3)
            # Save original filter
            orig_filter = sock.getsockopt(bt.SOL_HCI, bt.HCI_FILTER, 14)
            # Create new filter
            new_filter = bt.hci_filter_new()
            bt.hci_filter_set_ptype(new_filter, bt.HCI_EVENT_PKT)
            bt.hci_filter_set_event(new_filter, bt.EVT_CMD_COMPLETE)
            # CMD Read local name
            opcode = bt.cmd_opcode_pack(bt.OGF_HOST_CTL,
                                        bt.OCF_READ_LOCAL_NAME)
            bt.hci_filter_set_opcode(new_filter, opcode)
            sock.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, new_filter)
            try:
                bt.hci_send_cmd(sock, bt.OGF_HOST_CTL, bt.OCF_READ_LOCAL_NAME)
                data = sock.recv(255)
                name = data[7:].decode('utf-8')
                name = name[:name.find('\0')]
            except bt.timeout:
                print('bluetooth timeout during local device scan for name')
            except bt.error:
                print('bluetooth error during local device scan for name')
            # CMD Read local address
            opcode = bt.cmd_opcode_pack(bt.OGF_INFO_PARAM, bt.OCF_READ_BD_ADDR)
            bt.hci_filter_set_opcode(new_filter, opcode)
            sock.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, new_filter)
            try:
                bt.hci_send_cmd(sock, bt.OGF_INFO_PARAM, bt.OCF_READ_BD_ADDR)
                data = sock.recv(255)
                status, raw_bdaddr = struct.unpack('xxxxxxB6s', data)
                address = ['%02X' % b for b in raw_bdaddr]
                address.reverse()
                address = ':'.join(address)
            except bt.timeout:
                print('bluetooth timeout during local device scan for address')
            except bt.error:
                print('bluetooth error during local device scan for address')
            # Restore original filter
            sock.setsockopt(bt.SOL_HCI, bt.HCI_FILTER, orig_filter)
        sock.close()
        return name, address

    def get_device_name(self, address):
        """Retrieve device name"""
        return bluetooth.lookup_name(address)

    def get_classes(self, device_class):
        """Return device minor, major class and services class"""
        # Bits 02-07 Minor class bitwise
        minor_class = (device_class & 0xff) >> 2
        # Bits 08-12 Major class bitwise
        major_class = (device_class >> 8) & 0x1f
        # Bits 16-23 Service class
        services_class = (device_class >> 16)
        return minor_class, major_class, services_class

    def get_device_type(self, major_class):
        """Return the device major class"""
        if major_class not in MajorDeviceClasses.CLASSES:
            # Fallback to unknown class
            major_class = MajorDeviceClasses.UNKNOWN
        return MajorDeviceClasses.CLASSES[major_class]

    def get_device_detail(self, major_class, minor_class):
        """Return the device detail type or fallback to the unknown device"""
        return self.classes.get(major_class,
                                MajorDeviceClasses.UNKNOWN).get(
            minor_class,
            self.classes[MajorDeviceClasses.UNKNOWN][0])

    def get_services(self, address):
        """Return the list of the device's available services"""
        return bluetooth.find_service(address=address)

    def get_services_from_class(self, service_class):
        """Return the enabled services for a device class"""
        services = []
        service_classes = ServiceDeviceClasses.SERVICE_CLASSES
        for service, description in service_classes.items():
            if service_class & service:
                services.append(description)
        return services