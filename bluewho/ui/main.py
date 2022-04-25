##
#     Project: BlueWho
# Description: Information and notification of new discovered bluetooth devices
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2009-2022 Fabio Castelli
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

import time

from gi.repository import GLib, Gtk

from bluewho.bt.adapters import BluetoothAdapters
from bluewho.bt.device import BluetoothDevice
from bluewho.bt.device_discoverer import BluetoothDeviceDiscoverer
from bluewho.bt.support import BluetoothSupport
from bluewho.constants import (APP_NAME,
                               DOMAIN_NAME,
                               FILE_ICON,
                               FILE_SETTINGS,
                               USE_FAKE_DEVICES,
                               VERBOSE_LEVEL_NORMAL)
from bluewho.daemon_thread import DaemonThread
from bluewho.fake_devices import FakeDevices
from bluewho.functions import (_,
                               get_current_time,
                               process_events,
                               idle_add,
                               thread_safe)
from bluewho.preferences import (PREFERENCES_SCAN_SPEED,
                                 PREFERENCES_SHOW_LOCAL,
                                 PREFERENCES_STARTUPSCAN,
                                 Preferences)
from bluewho.settings import Settings
from bluewho.ui.about import DialogAbout
from bluewho.ui.base import UIBase
from bluewho.ui.message_dialog import (MessageDialogNoYes,
                                       MessageDialogOK,
                                       MessageDialogYesNo)
from bluewho.ui.model_devices import ModelDevices
from bluewho.ui.preferences import DialogPreferences
from bluewho.ui.services import DialogServices
from bluewho.ui.shortcuts import DialogShortcuts

SECTION_WINDOW_NAME = 'main window'


class MainWindow(UIBase):
    def __init__(self, application, options):
        super().__init__(filename='main.glade')
        self.application = application
        self.load_ui()
        self.settings = Settings(FILE_SETTINGS, True)
        self.preferences = Preferences(settings=self.settings)
        self.options = options
        self.btsupport = BluetoothSupport()
        self.discoverer = None
        self.model_devices = ModelDevices(self.ui.model_devices,
                                          self.settings,
                                          self.preferences,
                                          self.btsupport)
        # Initialize Gtk.HeaderBar
        self.set_buttons_icons(buttons=[self.ui.button_scan,
                                        self.ui.button_stop,
                                        self.ui.button_clear,
                                        self.ui.button_preferences,
                                        self.ui.button_services,
                                        self.ui.button_about,
                                        self.ui.button_options])
        # Set buttons with always show image
        for button in (self.ui.button_scan, ):
            button.set_always_show_image(True)
        self.ui.header_bar.props.title = self.ui.window.get_title()
        self.ui.window.set_titlebar(self.ui.header_bar)
        self.settings.restore_window_position(window=self.ui.window,
                                              section=SECTION_WINDOW_NAME)
        # Restore the devices list
        for device in self.settings.load_devices():
            self.add_device(name=device['name'],
                            address=device['address'],
                            device_class=device['class'],
                            last_seen=device['lastseen'],
                            notify=False)
        # Set other properties
        self.thread_scanner = None
        self.fake_devices = FakeDevices()

    def run(self):
        """Show the UI"""
        self.ui.window.show_all()
        # Activate scan on startup if Preferences.STARTUPSCAN is set
        if self.preferences.get(PREFERENCES_STARTUPSCAN):
            self.ui.action_scan.emit('activate')

    def load_ui(self):
        """Load the interface UI"""
        # Obtain widget references
        self.statusbar_context_id = self.ui.statusbar.get_context_id(
            DOMAIN_NAME)
        # Set various properties
        self.ui.window.set_title(APP_NAME)
        self.ui.window.set_icon_from_file(FILE_ICON)
        self.ui.window.set_application(self.application)
        # Connect signals from the glade file to the functions with the
        # same name
        self.ui.connect_signals(self)

    def on_window_delete_event(self, widget, event):
        """Close the application by closing the main window"""
        self.ui.action_quit.emit('activate')

    def on_action_about_activate(self, action):
        """Show the about dialog"""
        about = DialogAbout(parent=self.ui.window,
                            show=False)
        about.show()
        about.destroy()

    def on_action_options_menu_activate(self, widget):
        """Open the options menu"""
        self.ui.button_options.emit('clicked')

    def on_action_preferences_activate(self, action):
        """Show the preferences dialog"""
        dialog = DialogPreferences(self.preferences, self.ui.window, False)
        dialog.show()
        dialog.destroy()

    def on_action_services_activate(self, action):
        """Show the available services dialog for the selected device"""
        selected = self.ui.treeview_devices.get_selection().get_selected()[1]
        if selected:
            # Stop the scan to avoid locks
            self.ui.action_stop.emit('activate')
            # Get the device address
            address = self.model_devices.get_type(selected) == 'adapter' and \
                'localhost' or self.model_devices.get_address(selected)
            # Show the services dialog
            dialog = DialogServices(self.ui.window, False)
            # Load the list of enabled services
            for service in self.btsupport.get_services(address):
                dialog.model.add_service(service)
            dialog.show()

    def on_action_quit_activate(self, action):
        """Quit the application"""
        if self.thread_scanner:
            # Cancel the running thread
            if self.thread_scanner.is_alive():
                # Hide immediately the window and let the GTK+ cycle to
                # continue giving the perception that the app was really closed
                self.ui.window.hide()
                process_events()
                print('please wait for scan to complete...')
                self.ui.action_stop.emit('activate')
                process_events()
                time.sleep(10)
        self.thread_scanner = None
        self.settings.save_window_position(window=self.ui.window,
                                           section=SECTION_WINDOW_NAME)
        self.settings.save_devices(self.model_devices)
        self.settings.save()
        self.ui.window.destroy()
        self.model_devices.destroy()
        self.application.quit()

    def on_action_scan_activate(self, widget):
        if self.check_bluetooth_availability():
            # Start the scan
            self.ui.spinner.set_visible(True)
            self.ui.spinner.start()
            assert not self.thread_scanner
            self.thread_scanner = DaemonThread(self.do_scan, 'BTScanner')
            self.set_status_bar_message('Start new scan')
            self.thread_scanner.start()
            self.ui.action_scan.set_sensitive(False)

    def on_action_stop_activate(self, widget):
        if self.thread_scanner:
            # Check if the scanner is still running and cancel it
            if self.thread_scanner.is_alive():
                self.thread_scanner.cancel()
                self.set_status_bar_message('Cancel running scan')
            else:
                # The scanner thread has died for some error, we need to
                # recover the UI to allow the user to launch the scanner
                # again
                print('the thread has died, recovering the UI')
                self.set_status_bar_message(
                    'The scanning thread has died, recovering the UI')
                self.ui.spinner.stop()
                self.ui.spinner.set_visible(False)
                self.thread_scanner = None
                self.ui.action_scan.set_sensitive(True)

    def on_action_clear_activate(self, widget):
        """Clear the devices list"""
        dialog = MessageDialogNoYes(
            parent=self.ui.window,
            message_type=Gtk.MessageType.QUESTION,
            title=None,
            msg1=_('Do you want to clear the devices list?'),
            msg2=None)
        if dialog.run() == Gtk.ResponseType.YES:
            self.model_devices.clear()

    def add_device(self, name, address, device_class, last_seen, notify):
        """Add a device to the model in a thread safe way"""
        return self.add_device_safe(name,
                                    address,
                                    device_class,
                                    last_seen,
                                    notify)

    @thread_safe
    def add_device_safe(self, name, address, device_class, last_seen, notify):
        """Add a device to the model and optionally notify it"""
        if notify:
            # Add notification
            self.set_status_bar_message(
                'Found new device {NAME} [{ADDRESS}]'.format(NAME=name,
                                                             ADDRESS=address))
        self.model_devices.add_device(address=address,
                                      name=name,
                                      device_class=device_class,
                                      last_seen=last_seen,
                                      notify=notify)
        return False

    def do_scan(self):
        """Scan for bluetooth devices until cancelled"""
        # Find local adapters
        adapters = BluetoothAdapters.get_adapters()
        if adapters:
            # Discover devices via bluetooth
            if not self.discoverer:
                self.discoverer = BluetoothDeviceDiscoverer(
                    adapter=adapters[0],
                    timeout=self.preferences.get(PREFERENCES_SCAN_SPEED))
            while True:
                if self.preferences.get(PREFERENCES_SHOW_LOCAL):
                    # Only show local adapters when PREFERENCES_SHOW_LOCAL
                    # preference is set
                    for adapter in adapters:
                        self.add_device(name=f'{adapter.get_device_name()} '
                                             f'({adapter.get_name()})',
                                        address=adapter.get_address(),
                                        device_class=1 << 2,
                                        last_seen=get_current_time(),
                                        notify=True)
                # Cancel the running thread
                if self.thread_scanner.cancelled:
                    print('cancel')
                    self.discoverer.stop()
                    break
                # Wait until an event awakes the thread again
                if self.thread_scanner.paused:
                    self.thread_scanner.event.wait()
                    self.thread_scanner.event.clear()
                if self.discoverer.start():
                    # Discovery started
                    for item in self.discoverer.get_devices():
                        device = BluetoothDevice(device=item)
                        self.add_device(name=device.alias,
                                        address=device.address,
                                        device_class=device.device_class,
                                        last_seen=get_current_time(),
                                        notify=True)
                    # Add some fake devices for testing
                    if USE_FAKE_DEVICES:
                        self.fake_devices = FakeDevices()
                        for fake_device in self.fake_devices.fetch_many():
                            self.add_device(name=fake_device[0],
                                            address=fake_device[1],
                                            device_class=fake_device[2],
                                            last_seen=get_current_time(),
                                            notify=True)
                        time.sleep(2)
                else:
                    self.settings.logText(
                        'Discovery was aborted',
                        VERBOSE_LEVEL_NORMAL)
                    self.set_status_bar_message(
                        _('Discovery aborted.'))
        else:
            # No local adapters found
            self.settings.logText(
                'No local devices found during detection',
                VERBOSE_LEVEL_NORMAL)
            self.set_status_bar_message(
                _('No local devices found during detection.'))
        # After exiting from the scanning process, change the UI
        self.discoverer = None
        self.thread_scanner = None
        self.set_status_bar_message(None)
        idle_add(self.ui.spinner.stop)
        idle_add(self.ui.spinner.set_visible, False)
        idle_add(self.ui.action_scan.set_sensitive, True)
        return False

    def set_status_bar_message(self, message=None):
        """Set a new message in the status bar"""
        self.ui.statusbar.pop(self.statusbar_context_id)
        if message is not None:
            self.ui.statusbar.push(self.statusbar_context_id, message)

    def turn_on_adapters(self):
        """
        Try to power on every available adapter
        """
        for adapter in BluetoothAdapters.get_adapters():
            self.settings.logText('powering on adapter %s' %
                                  adapter.get_device_name())
            try:
                adapter.set_powered(status=True)
            except GLib.Error as e:
                # Intercept errors
                self.settings.logText(e)
                dialog_error = MessageDialogOK(
                    parent=self.ui.window,
                    message_type=Gtk.MessageType.WARNING,
                    title='Unable to start adapter %s' %
                          adapter.get_device_name(),
                    msg2=e.message,
                    msg1=None
                )
                dialog_error.run()

    def check_adapter_activation(self):
        """Check if any Bluetooth adapter is powered on"""
        adapters = BluetoothAdapters.get_adapters()
        result = False
        for adapter in adapters:
            if adapter.is_powered():
                # At least one adapter is powered on
                result = True
                break
        return result

    def on_action_shortcuts_activate(self, action):
        """Show the shortcuts dialog"""
        dialog = DialogShortcuts(parent=self.ui.window)
        dialog.show()

    def check_bluetooth_availability(self) -> bool:
        """
        Check Bluetooth availability

        :return: True if the bluetooth is enabled
        """
        result = False
        if not self.btsupport.is_bluez_available():
            # Bluez is not available
            self.settings.logText('Bluez is not available')
            dialog_error = MessageDialogOK(
                parent=self.ui.window,
                message_type=Gtk.MessageType.ERROR,
                title=None,
                msg1=_('Bluez seems not to be started, please make sure'
                       'the bluetooth service is started'),
                msg2=None
            )
            dialog_error.run()
        else:
            # Bluez is available, check the adapters activation
            if not self.check_adapter_activation():
                # No adapters are active
                dialog = MessageDialogYesNo(
                    parent=self.ui.window,
                    message_type=Gtk.MessageType.QUESTION,
                    title=None,
                    msg1=_('Do you want to start the bluetooth devices?'),
                    msg2=None)
                if dialog.run() == Gtk.ResponseType.YES:
                    self.turn_on_adapters()
                    result = self.check_adapter_activation()
            else:
                # At least one adapter is active
                result = True
        return result
