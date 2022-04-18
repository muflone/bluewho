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

from time import sleep

from gi.repository import GLib, Gtk

from bluewho.bt.adapters import BluetoothAdapters
from bluewho.constants import (APP_NAME,
                               DOMAIN_NAME,
                               FILE_ICON,
                               USE_FAKE_DEVICES,
                               VERBOSE_LEVEL_NORMAL)
from bluewho.daemon_thread import DaemonThread
from bluewho.fake_devices import FakeDevices
from bluewho.functions import (_,
                               get_current_time,
                               process_events,
                               idle_add,
                               thread_safe)
from bluewho.settings import Preferences
from bluewho.ui.about import DialogAbout
from bluewho.ui.base import UIBase
from bluewho.ui.message_dialog import (MessageDialogNoYes,
                                       MessageDialogOK,
                                       MessageDialogYesNo)
from bluewho.ui.model_devices import ModelDevices
from bluewho.ui.preferences import DialogPreferences
from bluewho.ui.services import DialogServices
from bluewho.ui.shortcuts import DialogShortcuts


class MainWindow(UIBase):
    def __init__(self, application, settings, btsupport):
        super().__init__(filename='main.glade')
        self.application = application
        self.settings = settings
        self.btsupport = btsupport
        self.is_refreshing = False
        self.loadUI()
        # Restore the saved size and position
        if self.settings.get_value(Preferences.RESTORE_SIZE):
            if self.settings.get_value(Preferences.WINWIDTH) and \
                    self.settings.get_value(Preferences.WINHEIGHT):
                self.ui.window_main.set_default_size(
                    self.settings.get_value(Preferences.WINWIDTH),
                    self.settings.get_value(Preferences.WINHEIGHT))
            if self.settings.get_value(Preferences.WINLEFT) and \
                    self.settings.get_value(Preferences.WINTOP):
                self.ui.window_main.move(
                    self.settings.get_value(Preferences.WINLEFT),
                    self.settings.get_value(Preferences.WINTOP))
        # Restore the devices list
        for device in self.settings.load_devices():
            self.add_device(device['address'],
                            device['name'],
                            device['class'],
                            device['lastseen'],
                            False)
        # Set other properties
        self.btsupport.set_new_device_cb(self.on_new_device_cb)
        self.thread_scanner = None
        self.fake_devices = FakeDevices()

    def run(self):
        """Show the UI"""
        self.ui.window_main.show_all()
        # Activate scan on startup if Preferences.STARTUPSCAN is set
        if self.settings.get_value(Preferences.STARTUPSCAN):
            self.ui.toolbutton_scan.set_active(True)

    def loadUI(self):
        """Load the interface UI"""
        self.ui = GtkBuilderLoader(get_ui_file('main.glade'))
        # Obtain widget references
        self.model_devices = ModelDevices(self.ui.model_devices,
                                          self.settings,
                                          self.btsupport)
        self.statusbar_context_id = self.ui.statusbar.get_context_id(
            DOMAIN_NAME)
        # Set various properties
        self.ui.window_main.set_title(APP_NAME)
        self.ui.window_main.set_icon_from_file(FILE_ICON)
        self.ui.window_main.set_application(self.application)
        # Connect signals from the glade file to the functions with the
        # same name
        self.ui.connect_signals(self)

    def on_window_main_delete_event(self, widget, event):
        """Close the application"""
        if self.thread_scanner:
            # Cancel the running thread
            if self.thread_scanner.is_alive():
                # Hide immediately the window and let the GTK+ cycle to
                # continue giving the perception that the app was really closed
                self.ui.window_main.hide()
                process_events()
                print('please wait for scan to complete...')
                self.thread_scanner.cancel()
                self.thread_scanner.join()
        self.thread_scanner = None
        # Save the position and size only if Preferences.RESTORE_SIZE is set
        if self.settings.get_value(Preferences.RESTORE_SIZE):
            self.settings.set_sizes(self.ui.window_main)
        self.settings.save_devices(self.model_devices)
        self.settings.save()
        self.ui.window_main.destroy()
        self.model_devices.destroy()
        self.application.quit()

    def on_toolbutton_about_clicked(self, widget):
        """Show the about dialog"""
        dialog = DialogAbout(self.ui.window_main, False)
        dialog.show()
        dialog.destroy()

    def on_toolbutton_scan_toggled(self, widget):
        """Reload the list of local and detected devices"""
        # Start the scanner thread
        if self.ui.toolbutton_scan.get_active():
            # Check if Bluez service is started
            if not self.btsupport.is_bluez_available():
                self.settings.logText('Bluez is not available')
                dialog_error = MessageDialogOK(
                    parent=self.ui.window_main,
                    message_type=Gtk.MessageType.ERROR,
                    title=None,
                    msg1=_('Bluez seems not to be started, please make sure'
                           'the bluetooth service is started'),
                    msg2=None
                )
                dialog_error.run()
                self.ui.toolbutton_scan.set_active(False)
            else:
                self.check_adapter_activation()
                # Start the scan
                self.ui.spinner.set_visible(True)
                self.ui.spinner.start()
                assert not self.thread_scanner
                self.thread_scanner = DaemonThread(self.do_scan, 'BTScanner')
                self.set_status_bar_message('Start new scan')
                self.thread_scanner.start()
        else:
            if self.thread_scanner:
                self.ui.toolbutton_scan.set_sensitive(False)
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
                    self.ui.toolbutton_scan.set_sensitive(True)

    def on_toolbutton_clear_clicked(self, widget):
        """Clear the devices list"""
        dialog = MessageDialogNoYes(
            parent=self.ui.window_main,
            message_type=Gtk.MessageType.QUESTION,
            title=None,
            msg1=_('Do you want to clear the devices list?'),
            msg2=None)
        if dialog.run() == Gtk.ResponseType.YES:
            self.model_devices.clear()

    def on_new_device_cb(self, name, address, device_class):
        """Callback function called when a new device has been discovered"""
        self.add_device(address,
                        name,
                        device_class,
                        get_current_time(),
                        True)

    @thread_safe
    def add_device(self, address, name, device_class, time, notify):
        """Add a device to the model and optionally notify it"""
        if notify:
            self.set_status_bar_message(
                'Found new device %s [%s]' % (name, address))
        self.model_devices.add_device(address,
                                      name,
                                      device_class,
                                      time,
                                      notify)
        return False

    def do_scan(self):
        """Scan for bluetooth devices until cancelled"""
        while True:
            # Cancel the running thread
            if self.thread_scanner.cancelled:
                break
            # Wait until an event awakes the thread again
            if self.thread_scanner.paused:
                self.thread_scanner.event.wait()
                self.thread_scanner.event.clear()
            # Only show local adapters when Preferences.SHOW_LOCAL
            # preference is set
            if self.settings.get_value(Preferences.SHOW_LOCAL):
                # Find local adapters
                adapters = BluetoothAdapters().get_adapters()
                if adapters:
                    # Local adapters found
                    for adapter in adapters:
                        self.add_device(adapter.get_address(),
                                        '%s (%s)' % (adapter.get_device_name(),
                                                     adapter.get_name()),
                                        1 << 2,
                                        get_current_time(),
                                        True)
                else:
                    # No local adapters found
                    self.settings.logText(
                        'No local devices found during detection',
                        VERBOSE_LEVEL_NORMAL)
                    self.set_status_bar_message(
                        _('No local devices found during detection.'))
                sleep(2)
            # Discover devices via bluetooth
            self.btsupport.discover(
                self.settings.get_value(Preferences.RETRIEVE_NAMES),
                self.settings.get_value(Preferences.SCAN_SPEED),
                True)

            # What is this? useful for testing purposes, you can just ignore it
            if USE_FAKE_DEVICES:
                self.fake_devices = FakeDevices()
                for fake_device in self.fake_devices.fetch_many():
                    self.on_new_device_cb(*fake_device)
                sleep(2)
        # After exiting from the scanning process, change the UI
        self.thread_scanner = None
        self.set_status_bar_message(None)
        idle_add(self.ui.spinner.stop)
        idle_add(self.ui.spinner.set_visible, False)
        idle_add(self.ui.toolbutton_scan.set_sensitive, True)
        return False

    def on_toolbutton_services_clicked(self, widget):
        """Show the available services dialog for the selected device"""
        selected = self.ui.treeview_devices.get_selection().get_selected()[1]
        if selected:
            # Stop the scan to avoid locks
            self.ui.toolbutton_scan.set_active(False)
            # Get the device address
            address = self.model_devices.get_type(selected) == 'adapter' and \
                'localhost' or self.model_devices.get_address(selected)
            # Show the services dialog
            dialog = DialogServices(self.ui.window_main, False)
            # Load the list of enabled services
            for service in self.btsupport.get_services(address):
                dialog.model.add_service(service)
            dialog.show()

    def on_toolbutton_preferences_clicked(self, widget):
        """Show the preferences dialog"""
        dialog = DialogPreferences(self.settings, self.ui.window_main, False)
        dialog.show()

    @thread_safe
    def set_status_bar_message(self, message=None):
        """Set a new message in the status bar"""
        self.ui.statusbar.pop(self.statusbar_context_id)
        if message is not None:
            self.ui.statusbar.push(self.statusbar_context_id, message)

    def check_adapter_activation(self):
        """Check if any Bluetooth adapter is powered on"""
        adapters = BluetoothAdapters().get_adapters()
        for adapter in adapters:
            if adapter.is_powered():
                # At least one adapter is powered on
                break
        else:
            # No powered on adapters
            dialog = MessageDialogYesNo(
                parent=self.ui.window_main,
                message_type=Gtk.MessageType.QUESTION,
                title=None,
                msg1=_('Do you want to start the bluetooth devices?'),
                msg2=None)
            if dialog.run() == Gtk.ResponseType.YES:
                # Try to power on every adapter
                for adapter in adapters:
                    self.settings.logText('powering on adapter %s' %
                                          adapter.get_device_name())
                    try:
                        adapter.set_powered(status=True)
                    except GLib.Error as e:
                        # Intercept errors
                        self.settings.logText(e)
                        dialog_error = MessageDialogOK(
                            parent=self.ui.window_main,
                            message_type=Gtk.MessageType.WARNING,
                            title='Unable to start adapter %s' %
                                  adapter.get_device_name(),
                            msg2=e.message,
                            msg1=None
                        )
                        dialog_error.run()

    def on_toolbutton_shortcuts_clicked(self, widget):
        """Show the shortcuts dialog"""
        dialog = DialogShortcuts(parent=self.ui.window_main)
        dialog.show()
