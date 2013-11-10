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

import os
import os.path
import subprocess

class AudioPlayer(object):
  def __init__(self):
    "Initialize audio players"
    self.players = {
      'canberra-gtk-play': ('-f', '%s'),
      'aplay': ('-q', '%s'),
      'paplay': ('-p', '%s'),
      'mplayer': ('-really-quiet', '%s'),
    }
    self.player = None
    self.player_path = None
    self.detect_player()

  def which(self, program):
    "Determine the full path of an executable program"
    def is_exe(fpath):
      "Check if fpath is an executable file"
      return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
      # Check for direct file path
      if is_exe(program):
        return program
    else:
      # Check the file in the PATH environment variable's paths
      for path in os.environ['PATH'].split(os.pathsep):
        path = path.strip('"')
        exe_file = os.path.join(path, program)
        if is_exe(exe_file):
          return exe_file
    # Path not found
    return None

  def detect_player(self):
    "Find an executable audio player"
    for program in self.players.iterkeys():
      program_path = self.which(program)
      if program_path:
        self.player = program
        self.player_path = program_path
        break

  def play_file(self, audio_file):
    "Play an audio file with the detected audio player"
    if self.player:
      arguments = [self.player_path]
      for option in self.players[self.player]:
        arguments.append(option == '%s' and audio_file or option)
      # Execute external process
      proc = subprocess.Popen(arguments,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
