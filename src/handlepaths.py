##
#   Project: bluewho
#            Information and notification of new discovered bluetooth devices.
#    Author: Fabio Castelli <muflone@vbsimple.net>
# Copyright: 2009 Fabio Castelli
#   License: GPL-2+
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation; either version 2 of the License, or (at your option)
#  any later version.
# 
#  This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
# 
# On Debian GNU/Linux systems, the full text of the GNU General Public License
# can be found in the file /usr/share/common-licenses/GPL-2.
##

import os
import sys

base_path = os.path.dirname(os.path.abspath(__file__))
APP_NAME = 'bluewho'
APP_TITLE = 'BlueWho'
APP_VERSION = '0.1'

PATHS = {
  'locale': [
    '%s/../locale' % base_path,
    '%s/share/locale' % sys.prefix],
  'data': [
    '%s/../data' % base_path,
    '%s/share/%s/data' % (sys.prefix, APP_NAME)],
  'gfx': [
    '%s/../gfx' % base_path,
    '%s/share/%s/gfx' % (sys.prefix, APP_NAME)],
  'doc': [
    '%s/../doc' % base_path,
    '%s/share/doc/%s' % (sys.prefix, APP_NAME)]
}

def getPath(key, append = ''):
  "Returns the correct path for the specified key"
  for path in PATHS[key]:
    if os.path.isdir(path):
      if append:
        return os.path.abspath(os.path.join(path, append))
      else:
        return os.path.abspath(path)

def get_app_logo():
  "Returns the path of the icon logo"
  return getPath('data', '%s.svg' % APP_NAME)
