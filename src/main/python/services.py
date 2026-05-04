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
        try:
            super().__init__(
                real_device.address, 
                real_device.name, 
                real_device.details, 
                getattr(real_device, 'rssi', -60)
            )
        except TypeError:
            super().__init__(
                real_device.address, 
                real_device.name, 
                real_device.details
            )
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
            max_retries = 3
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    # 1. Scan for the device
                    real_device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)
                    
                    # --- THE HAMMER FALLBACK ---
                    if real_device is None:
                        print(f"Device {mac_address} not found. Bouncing Bluetooth adapter...")
                        os.system("sudo bluetoothctl power off && sudo bluetoothctl power on")
                        await asyncio.sleep(3.0) 
                        real_device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)
                    # ---------------------------

                    if real_device is None:
                        raise Exception(f"Could not discover Switchbot at {mac_address}. Is it in range?")

                    # 2. Wrap it and initialize
                    patched_device = PatchedBLEDevice(real_device)
                    bot = Switchbot(device=patched_device)

                    # 3. Perform the action
                    if action == 'on':
                        await bot.turn_on()
                    elif action == 'off':
                        await bot.turn_off()
                    elif action == 'press':
                        await bot.press()
                    else:
                        raise ValueError(f"Invalid action '{action}'. Use 'on', 'off', or 'press'.")

                    # --- SUCCESS! ---
                    # Give BlueZ time to cleanly disconnect, then exit the function immediately.
                    await asyncio.sleep(2.0)
                    return 
                    # ----------------

                except Exception as e:
                    # Catch the bytearray error (or any other BLE timeout) and try again
                    last_error = e
                    print(f"Attempt {attempt + 1}/{max_retries} failed: {e}. Retrying...")
                    await asyncio.sleep(2.0)
            
            # If we loop 3 times and still fail, throw the error back to the Flask API
            raise Exception(f"Action failed after {max_retries} attempts. Last error: {str(last_error)}")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(perform_action())
        finally:
            loop.close()
            
        return mac_address

