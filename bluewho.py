import gettext
import locale
from bluewho.settings import Settings
from bluewho.btsupport import BluetoothSupport
from bluewho.app import Application
from bluewho.constants import *

if __name__ == '__main__':
  # Load domain for translation
  for module in (gettext, locale):
    module.bindtextdomain(DOMAIN_NAME, DIR_LOCALE)
    module.textdomain(DOMAIN_NAME)

  # Load the settings from the configuration file
  settings = Settings()
  settings.load()

  # Create BluetoothSupport instance
  btsupport = BluetoothSupport()
  # Start the application
  app = Application(settings, btsupport)
  app.run(None)
