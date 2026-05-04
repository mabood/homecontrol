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

# Safely patches the missing properties from older bleak versions
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
        
        if len(self.devices) != 0:
            # 1. Create a dedicated event loop for Bluetooth operations
            self.loop = asyncio.new_event_loop()
            
            # 2. Start it in a background thread that NEVER dies
            self.ble_thread = threading.Thread(target=self._start_background_loop, args=(self.loop,), daemon=True)
            self.ble_thread.start()

    def _start_background_loop(self, loop):
        """This runs forever in the background, keeping bleak's D-Bus connections healthy."""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    async def _async_operate(self, name: str, action: str) -> str:
        """The actual asynchronous hardware logic running on the background thread."""
        mac_address = self.devices[name]

        real_device = await BleakScanner.find_device_by_address(mac_address, timeout=10.0)
        
        if real_device is None:
            raise Exception(f"Could not discover Switchbot at {mac_address}. Is it in range?")

        patched_device = PatchedBLEDevice(real_device)
        bot = Switchbot(device=patched_device)

        if action == 'on':
            await bot.turn_on()
        elif action == 'off':
            await bot.turn_off()
        elif action == 'press':
            await bot.press()
        else:
            raise ValueError(f"Invalid action '{action}'. Use 'on', 'off', or 'press'.")

        # Give BlueZ a moment to process the D-Bus disconnection gracefully
        await asyncio.sleep(1.0)
        return mac_address

    def operate_switchbot(self, name: str, action: str) -> str:
        """The synchronous method called by your Flask route."""
        if name not in self.devices:
            raise KeyError(f"Device '{name}' not found in config")
            
        # 3. Hand the task over to the permanent background thread safely
        future = asyncio.run_coroutine_threadsafe(
            self._async_operate(name, action), 
            self.loop
        )
        
        # 4. Block the Flask web thread until the background thread finishes
        # This will either return the mac_address, or raise any Exceptions that occurred
        return future.result()
