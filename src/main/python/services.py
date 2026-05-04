#
# Home Control - Services
# Created by Michael Abood on 04/19/20
#
#    This file is part of Home Control.
#
#    Home Control is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Home Control is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Home Control.  If not, see <https://www.gnu.org/licenses/>.
#

import os
import logging
import constants
import sensors
import miniaudio
import asyncio
from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from switchbot import Switchbot

class Chime(object):
    _stream = None
    _device = None

    def __init__(self, config, resources_dir, filename):
        capabilities = config[constants.CONFIG_SECTION_CAPABILITIES]
        if not eval(capabilities['speaker_enabled']):
            logging.error('Cannot play \'%s\' - speaker is not enabled in configuration. See README for setup instructions', filename)
            return None
        self.resources_dir = resources_dir
        self._stream = miniaudio.stream_file(os.path.join(resources_dir, filename))
        self._device = miniaudio.PlaybackDevice()

    def ring(self):
        if self._device is not None:
            # Plays the sound file in a background thread
            self._device.start(self._stream)

# --- THE BULLETPROOF WRAPPER ---
# The rssi error: Even in version 0.37.0, if you pass a MAC address string, 
# PySwitchbot gets a BLEDevice from the Pi's older bleak library 
# (which lacks an rssi attribute), checks for device.rssi, and crashes.
class PatchedBLEDevice(BLEDevice):
    def __init__(self, real_device):
        # We pass the REAL details dictionary from Linux to prevent the 'NoneType' error
        try:
            # Try modern bleak format
            super().__init__(
                real_device.address, 
                real_device.name, 
                real_device.details, 
                getattr(real_device, 'rssi', -60)
            )
        except TypeError:
            # Fall back to older bleak format
            super().__init__(
                real_device.address, 
                real_device.name, 
                real_device.details
            )
        
        # Because we subclassed, we bypass the __slots__ memory lock 
        # and can force the rssi attribute onto the object!
        self.rssi = getattr(real_device, 'rssi', -60)
# -------------------------------

class SwitchbotController:
    def __init__(self, config):
        """
        Initializes the service and pre-loads the device mappings 
        from the application configuration.
        """
        self.devices = dict(config[constants.CONFIG_SECTION_SWITCHBOT]) if config.has_section(constants.CONFIG_SECTION_SWITCHBOT) else {}

    def operate_switchbot(self, name: str, action: str) -> str:
        if name not in self.devices:
            raise KeyError(f"Device '{name}' not found in config")
            
        mac_address = self.devices[name]

        async def perform_action():
            # 1. Let Linux find the REAL device (Gets the actual routing 'details')
            real_device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)
            
            if real_device is None:
                raise Exception(f"Could not discover Switchbot at {mac_address}. Is it in range?")

            # 2. Wrap it to forcefully attach the missing 'rssi' attribute
            patched_device = PatchedBLEDevice(real_device)

            # 3. Hand the heavily armored object to PySwitchbot using 'device='
            bot = Switchbot(device=patched_device)

            if action == 'on':
                await bot.turn_on()
            elif action == 'off':
                await bot.turn_off()
            elif action == 'press':
                await bot.press()
            else:
                raise ValueError(f"Invalid action '{action}'. Use 'on', 'off', or 'press'.")

        # Safely create a new event loop for this Flask thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(perform_action())
        finally:
            loop.close()
            
        return mac_address

