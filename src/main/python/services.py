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

class SwitchbotController:
    def __init__(self, config: dict):
        """
        Initializes the service and pre-loads the device mappings 
        from the application configuration.
        """
        # Store the devices dictionary directly for faster lookups
        self.devices = config[constants.CONFIG_SECTION_CAPABILITIES].get("switchbot", {})

    async def operate_switchbot(self, name: str, action: str) -> str:
        """
        Looks up a Switchbot by name, connects via BLE, 
        and performs the requested action.
        
        Returns the MAC address upon success, or raises an error.
        """
        # 1. Look up the device MAC address from the pre-loaded dictionary
        if name not in self.devices:
            raise KeyError(f"Device '{name}' not found in config")
            
        mac_address = self.devices[name]
        
        # 2. Initialize the bot
        bot = Switchbot(mac=mac_address)

        # 3. Perform the action
        if action == 'on':
            await bot.turn_on()
        elif action == 'off':
            await bot.turn_off()
        elif action == 'press':
            await bot.press()
        else:
            raise ValueError(f"Invalid action '{action}'. Use 'on', 'off', or 'press'.")
            
        return mac_address
