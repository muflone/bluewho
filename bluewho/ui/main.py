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

import logging
import time

from gi.repository import GLib, Gtk

from bluewho.bt.adapters import BluetoothAdapters
from bluewho.bt.device import BluetoothDevice
from bluewho.bt.device_discoverer import BluetoothDeviceDiscoverer
from bluewho.bt.support import BluetoothSupport
from bluewho.constants import (APP_DOMAIN,
                               APP_NAME,
                               FILE_ICON,
                               FILE_SETTINGS)
from bluewho.daemon_thread import DaemonThread
from bluewho.fake_devices import FakeDevices
from bluewho.functions import (get_current_time,
                               process_events,
                               idle_add,
                               thread_safe)
from bluewho.localize import _, text_gtk30
from bluewho.models.device_info import DeviceInfo
from bluewho.settings import (PREFERENCES_NOTIFICATION,
                              PREFERENCES_PLAY_SOUND,
                              PREFERENCES_SCAN_SPEED,
                              PREFERENCES_SHOW_LOCAL,
                              PREFERENCES_STARTUPSCAN,
                              Settings)
from bluewho.ui.about import UIAbout
from bluewho.ui.base import UIBase
from bluewho.ui.message_dialog import (MessageDialogNoYes,
                                       MessageDialogOK,
                                       MessageDialogYesNo)
from bluewho.ui.model_devices import ModelDevices
from bluewho.ui.shortcuts import UIShortcuts

SECTION_WINDOW_NAME = 'main window'


class UIMain(UIBase):
    def __init__(self, application, options):
        """Prepare the main window"""
        logging.debug(f'{self.__class__.__name__} init')
        super().__init__(filename='main.ui')
        # Initialize members
        self.application = application
        self.options = options
        self.thread_scanner = None
        self.btsupport = BluetoothSupport()
        self.discoverer = None
        # Load settings
        self.settings = Settings(filename=FILE_SETTINGS,
                                 case_sensitive=True)
        self.settings.load_preferences()
        self.settings_map = {}
        self.settings_scan_speed_map = {}
        # Load UI
        self.load_ui()
        # Prepare the models
        self.model_devices = ModelDevices(self.ui.model_devices,
                                          self.settings,
                                          self.btsupport)
        # Complete initialization
        self.startup()

    def load_ui(self):
        """Load the interface UI"""
        logging.debug(f'{self.__class__.__name__} load UI')
        # Initialize translations
        self.ui.action_about.set_label(text_gtk30('About'))
        # Initialize titles and tooltips
        self.set_titles()
        # Initialize Gtk.HeaderBar
        self.ui.header_bar.props.title = self.ui.window.get_title()
        self.ui.window.set_titlebar(self.ui.header_bar)
        self.set_buttons_icons(buttons=[self.ui.button_scan,
                                        self.ui.button_stop,
                                        self.ui.button_clear,
                                        self.ui.button_about,
                                        self.ui.button_options])
        # Set buttons with always show image
        for button in (self.ui.button_scan, ):
            button.set_always_show_image(True)
        self.set_buttons_style_suggested_action(
            buttons=[self.ui.button_scan])
        # Set various properties
        self.ui.window.set_title(APP_NAME)
        self.ui.window.set_icon_from_file(str(FILE_ICON))
        self.ui.window.set_application(self.application)
        # Connect signals from the UI file to the functions with the same name
        self.ui.connect_signals(self)

    def startup(self):
        """Complete initialization"""
        logging.debug(f'{self.__class__.__name__} startup')
        self.settings_map = {
            PREFERENCES_NOTIFICATION:
                self.ui.action_options_notification_show,
            PREFERENCES_PLAY_SOUND:
                self.ui.action_options_notification_play_sound,
            PREFERENCES_SHOW_LOCAL:
                self.ui.action_options_show_local_adapters,
            PREFERENCES_STARTUPSCAN:
                self.ui.action_options_startup_scan,
        }
        # Load settings
        for setting_name, action in self.settings_map.items():
            action.set_active(self.settings.get_preference(
                option=setting_name))
        self.settings_scan_speed_map = {
            4: self.ui.action_options_scan_speed_high,
            8: self.ui.action_options_scan_speed_medium,
            12: self.ui.action_options_scan_speed_low
        }
        scan_speed = self.settings.get_preference(
            option=PREFERENCES_SCAN_SPEED)
        if scan_speed in self.settings_scan_speed_map:
            self.settings_scan_speed_map.get(
                scan_speed,
                self.ui.action_options_scan_speed_medium).set_active(True)
        # Restore the devices list
        for device in self.settings.load_devices():
            self.do_add_device(device)
        if len(self.model_devices) > 0:
            self.ui.treeview_devices.set_cursor(0)
        self.ui.treeview_devices.grab_focus()
        # Restore the saved size and position
        self.settings.restore_window_position(window=self.ui.window,
                                              section=SECTION_WINDOW_NAME)

    def run(self):
        """Show the UI"""
        logging.debug(f'{self.__class__.__name__} run')
        self.ui.window.show_all()
        # Activate scan on startup if Preferences.STARTUPSCAN is set
        if self.settings.get_preference(option=PREFERENCES_STARTUPSCAN):
            self.ui.action_scan.activate()

    @thread_safe
    def do_add_device(self, device: DeviceInfo):
        """Add a device to the model and optionally notify it"""
        if device.notify and device.address not in self.model_devices.rows:
            # Add notification
            self.do_set_status_bar_message(
                _('New device found: {NAME} [{ADDRESS}]').format(
                    NAME=device.name,
                    ADDRESS=device.address))
        self.model_devices.add_data(device=device)
        return False

    def do_check_adapter_activation(self):
        """Check if any Bluetooth adapter is powered on"""
        result = False
        adapters = BluetoothAdapters.get_adapters()
        for adapter in adapters:
            if adapter.is_powered():
                # At least one adapter is powered on
                result = True
                break
        return result

    def do_check_bluetooth_availability(self) -> bool:
        """
        Check Bluetooth availability

        :return: True if the bluetooth is enabled
        """
        result = False
        if not self.btsupport.is_bluez_available():
            # Bluez is not available
            logging.error('Bluez is not available')
            dialog = MessageDialogOK(
                parent=self.ui.window,
                message_type=Gtk.MessageType.ERROR,
                title='',
                msg1=_('Bluez seems not to be started, please make sure '
                       'the bluetooth service is started'),
                msg2=None)
            dialog.run()
        else:
            # Bluez is available, check the adapters activation
            if not self.do_check_adapter_activation():
                # No adapters are active
                dialog = MessageDialogYesNo(
                    parent=self.ui.window,
                    message_type=Gtk.MessageType.QUESTION,
                    title='',
                    msg1=_('Do you want to start the bluetooth devices?'),
                    msg2=None)
                if dialog.run() == Gtk.ResponseType.YES:
                    self.do_turn_on_adapters()
                    result = self.do_check_adapter_activation()
            else:
                # At least one adapter is active
                result = True
        return result

    def do_scan(self):
        """Scan for bluetooth devices until cancelled"""
        # Find local adapters
        adapters = BluetoothAdapters.get_adapters()
        if adapters or self.options.fake_devices:
            if self.options.fake_devices:
                # Add some fake devices
                fake_devices = FakeDevices()
            else:
                # Discover devices via bluetooth
                if not self.discoverer:
                    self.discoverer = BluetoothDeviceDiscoverer(
                        adapter=adapters[0],
                        timeout=self.settings.get_preference(
                            option=PREFERENCES_SCAN_SPEED))
                fake_devices = None
            while True:
                if (self.settings.get_preference(option=PREFERENCES_SHOW_LOCAL)
                        and not self.options.fake_devices):
                    # Only show local adapters when PREFERENCES_SHOW_LOCAL
                    # preference is set and not using fake devices
                    for adapter in adapters:
                        device = DeviceInfo(address=adapter.get_address(),
                                            name=f'{adapter.get_device_name()}'
                                                 f' ({adapter.get_name()})',
                                            device_class=1 << 2,
                                            last_seen=get_current_time(),
                                            notify=True)
                        self.do_add_device(device)
                if not self.thread_scanner:
                    # Abort scan per removed thread
                    logging.warning('thread removed')
                    if self.discoverer:
                        self.discoverer.stop()
                    break
                elif self.thread_scanner.cancelled:
                    # Cancel the running thread
                    logging.info('Discovery canceled')
                    if self.discoverer:
                        self.discoverer.stop()
                    break
                # Wait until an event awakes the thread again
                if self.thread_scanner.paused:
                    self.thread_scanner.event.wait()
                    self.thread_scanner.event.clear()
                if self.options.fake_devices:
                    # Add some fake devices
                    devices = fake_devices.fetch_max(self.options.fake_devices)
                    for device in devices:
                        self.do_add_device(device)
                    time.sleep(self.settings.get_preference(
                        option=PREFERENCES_SCAN_SPEED))
                else:
                    # Start the discovery
                    if self.discoverer.start():
                        for item in self.discoverer.get_devices():
                            device = BluetoothDevice(device=item)
                            self.do_add_device(device.to_device_info())
                    else:
                        logging.info('Discovery was aborted')
                        self.do_set_status_bar_message(_('Discovery aborted.'))
        else:
            # No local adapters found
            logging.info('No local devices found during detection')
            self.do_set_status_bar_message(
                _('No local devices found during detection.'))
        # After exiting from the scanning process, change the UI
        self.discoverer = None
        self.thread_scanner = None
        self.do_set_status_bar_message(None)
        idle_add(self.ui.spinner.stop)
        idle_add(self.ui.spinner.set_visible, False)
        idle_add(self.ui.action_scan.set_sensitive, True)
        return False

    def do_set_status_bar_message(self, message=None):
        """Set a new message in the status bar"""
        statusbar_context_id = self.ui.statusbar.get_context_id(APP_DOMAIN)
        self.ui.statusbar.pop(statusbar_context_id)
        if message is not None:
            self.ui.statusbar.push(statusbar_context_id, message)

    def do_turn_on_adapters(self):
        """
        Try to power on every available adapter
        """
        adapters = BluetoothAdapters.get_adapters()
        if adapters:
            for adapter in adapters:
                logging.info('powering on adapter '
                             f'{adapter.get_device_name()}')
                try:
                    adapter.set_powered(status=True)
                except GLib.Error as e:
                    # Intercept errors
                    logging.error(e)
                    dialog = MessageDialogOK(
                        parent=self.ui.window,
                        message_type=Gtk.MessageType.WARNING,
                        title='Unable to start adapter '
                              f'{adapter.get_device_name()}',
                        msg1=None,
                        msg2=e.message)
                    dialog.run()
        else:
            # No local adapters found
            dialog = MessageDialogOK(
                parent=self.ui.window,
                message_type=Gtk.MessageType.WARNING,
                title='',
                msg1=_('No local devices found during detection.'),
                msg2=None)
            dialog.run()

    def on_action_about_activate(self, widget):
        """Show the information dialog"""
        dialog = UIAbout(parent=self.ui.window,
                         settings=self.settings,
                         options=self.options)
        dialog.show()
        dialog.destroy()

    def on_action_shortcuts_activate(self, widget):
        """Show the shortcuts dialog"""
        dialog = UIShortcuts(parent=self.ui.window,
                             settings=self.settings,
                             options=self.options)
        dialog.show()

    def on_action_quit_activate(self, widget):
        """Save the settings and close the application"""
        logging.debug(f'{self.__class__.__name__} quit')
        if self.thread_scanner:
            # Cancel the running thread
            if self.thread_scanner.is_alive():
                # Hide immediately the window and let the GTK+ cycle to
                # continue giving the perception that the app was really closed
                self.ui.window.hide()
                process_events()
                logging.info('please wait for scan to complete...')
                self.ui.action_stop.activate()
        self.settings.save_window_position(window=self.ui.window,
                                           section=SECTION_WINDOW_NAME)
        self.settings.save_devices(self.model_devices)
        self.settings.save()
        self.ui.window.destroy()
        self.model_devices.destroy()
        self.application.quit()

    def on_action_options_menu_activate(self, widget):
        """Open the options menu"""
        self.ui.button_options.clicked()

    def on_action_options_toggled(self, widget):
        """Change an option value"""
        for setting_name, item in self.settings_map.items():
            if item is widget:
                self.settings.set_preference(option=setting_name,
                                             value=item.get_active())

    def on_action_options_scan_speed_activate(self, widget):
        """Change scan speed"""
        for speed, item in self.settings_scan_speed_map.items():
            if item is widget and widget.get_active():
                self.settings.set_preference(option=PREFERENCES_SCAN_SPEED,
                                             value=speed)

    def on_action_scan_activate(self, widget):
        if self.do_check_bluetooth_availability() or self.options.fake_devices:
            # Start the scan
            self.ui.spinner.set_visible(True)
            self.ui.spinner.start()
            assert not self.thread_scanner
            self.thread_scanner = DaemonThread(self.do_scan, 'BTScanner')
            self.do_set_status_bar_message(_('Detect devices'))
            self.thread_scanner.start()
            self.ui.action_scan.set_sensitive(False)

    def on_action_stop_activate(self, widget):
        if self.thread_scanner:
            # Check if the scanner is still running and cancel it
            if self.thread_scanner.is_alive():
                self.thread_scanner.cancel()
                self.do_set_status_bar_message(_('Stop detection'))
            else:
                # The scanner thread has died for some error, we need to
                # recover the UI to allow the user to launch the scanner
                # again
                logging.error('the thread has died, recovering the UI')
                self.do_set_status_bar_message(
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
            title='',
            msg1=_('Do you want to clear the devices list?'),
            msg2=None)
        if dialog.run() == Gtk.ResponseType.YES:
            logging.debug('Clearing results list')
            self.model_devices.clear()

    def on_window_delete_event(self, widget, event):
        """Close the application by closing the main window"""
        logging.debug(f'{self.__class__.__name__} delete')
        self.ui.action_quit.activate()
