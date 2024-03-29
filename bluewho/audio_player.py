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

import os
import os.path
import subprocess


class AudioPlayer(object):
    def __init__(self):
        """Initialize audio players"""
        self.players = {
          'canberra-gtk-play': ('-f', '{FILENAME}'),
          'aplay': ('-q', '{FILENAME}'),
          'paplay': ('-p', '{FILENAME}'),
          'mplayer': ('-really-quiet', '{FILENAME}'),
        }
        self.player = None
        self.player_path = None
        self.detect_player()

    def which(self, program):
        """Determine the full path of an executable program"""
        def is_exe(file_path):
            """Check if fpath is an executable file"""
            return os.path.isfile(file_path) and os.access(file_path, os.X_OK)

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
        """Find an executable audio player"""
        for program in self.players:
            program_path = self.which(program)
            if program_path:
                self.player = program
                self.player_path = program_path
                break

    def play_file(self, audio_file):
        """Play an audio file with the detected audio player"""
        if self.player:
            arguments = [self.player_path]
            for option in self.players[self.player]:
                arguments.append(audio_file
                                 if option == '{FILENAME}'
                                 else option)
            # Execute external process
            subprocess.Popen(arguments,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
