 #!/usr/bin/env python
###########################################################################
# odb_io.py
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
#
# This file is part of pyOBD.
#
# pyOBD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################
# Updated to Python 3 using Ai by Rufus Brandes 2025
#
###########################################################################


import string  # Missing import added
import time  # Ensure time is imported
import serial  # Importing serial as it's used extensively


class OBDPort:
    """ OBDPort abstracts all communication with OBD-II device."""

    def __init__(self, portnum, _notify_window, SERTIMEOUT, RECONNATTEMPTS):
        """Initializes port by resetting device and getting supported PIDs."""
        # These should really be set by the user.
        baud = 38400
        databits = 8
        par = serial.PARITY_NONE  # parity
        sb = 1  # stop bits
        to = SERTIMEOUT
        self.ELMver = "Unknown"
        self.State = 1  # state SERIAL is 1 connected, 0 disconnected (connection failed)
        self.port = None

        self._notify_window = _notify_window
        debug_display(self._notify_window, 1, "Opening interface (serial port)")

        try:
            self.port = serial.Serial(portnum, baud,
                                      parity=par, stopbits=sb, bytesize=databits, timeout=to)

        except serial.SerialException as e:
            print(e)  # Fixed missing parentheses
            self.State = 0
            return None

        debug_display(self._notify_window, 1, "Interface successfully " + self.port.portstr + " opened")
        debug_display(self._notify_window, 1, "Connecting to ECU...")

        try:
            self.send_command("atz")  # initialize
            time.sleep(1)
        except serial.SerialException:
            self.State = 0
            return None

        self.ELMver = self.get_result()
        if self.ELMver is None:
            self.State = 0
            return None

        debug_display(self._notify_window, 2, "atz response:" + self.ELMver)
        self.send_command("ate0")  # echo off
        debug_display(self._notify_window, 2, "ate0 response:" + self.get_result())
        self.send_command("0100")
        ready = self.get_result()

        if ready is None:
            self.State = 0
            return None

        debug_display(self._notify_window, 2, "0100 response:" + ready)
        return None

    def close(self):
        """ Resets device and closes all associated file handles"""

        if self.port is not None and self.State == 1:
            self.send_command("atz")
            self.port.close()

        self.port = None
        self.ELMver = "Unknown"

    def send_command(self, cmd):
        """Internal use only: not a public interface"""
        if self.port:
            self.port.flushOutput()
            self.port.flushInput()
            for c in cmd:
                self.port.write(c.encode())  # Python 3: encode to bytes
            self.port.write("\r\n".encode())

    def interpret_result(self, code):
        """Internal use only: not a public interface"""
        # Code will be the string returned from the device.
        # It should look something like this:
        # '41 11 0 0\r\r'

        # 9 seems to be the length of the shortest valid response
        if len(code) < 7:
            # raise Exception("BogusCode")
            print("boguscode?" + code)  # Fixed missing parentheses

        # get the first thing returned, echo should be off
        code = string.split(code, "\r")
        code = code[0]

        # remove whitespace
        code = string.split(code)
        code = "".join(code)  # Use join for Python 3

        # cables can behave differently
        if code[:6] == "NODATA":  # there is no such sensor
            return "NODATA"

        # first 4 characters are code from ELM
        code = code[4:]
        return code

    def get_result(self):
        """Internal use only: not a public interface"""
        # time.sleep(0.01)
        repeat_count = 0
        if self.port is not None:
            buffer = ""
            while True:
                c = self.port.read(1).decode()  # Python 3: decode bytes
                if len(c) == 0:
                    if repeat_count == 5:
                        break
                    print("Got nothing\n")  # Fixed missing parentheses
                    repeat_count += 1
                    continue

                if c == '\r':
                    continue

                if c == ">":
                    break

                if buffer != "" or c != ">":  # if something is in buffer, add everything
                    buffer = buffer + c

            # debug_display(self._notify_window, 3, "Get result:" + buffer)
            if buffer == "":
                return None
            return buffer
        else:
            debug_display(self._notify_window, 3, "NO self.port!")
        return None
