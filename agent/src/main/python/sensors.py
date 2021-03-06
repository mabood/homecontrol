#
# Home Control - Sensors
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

import logging
import os

CONFIG_KEY_THERMOMETER_ENABLED = 'thermometer_enabled'
CONFIG_KEY_THERMOMETER_DIR = 'thermometer_device_dir'
CONFIG_KEY_THERMOMETER_FILE = 'thermometer_device_file'


class Thermometer(object):
    @staticmethod
    def make(sensors_config):
        if not eval(sensors_config[CONFIG_KEY_THERMOMETER_ENABLED]):
            logging.error('Thermometer is not enabled in configs.')
            return None
        try:
            return Thermometer(sensors_config[CONFIG_KEY_THERMOMETER_DIR], 
                               sensors_config[CONFIG_KEY_THERMOMETER_FILE])
        except Exception as e:
            logging.error('Thermometer is enabled in configs, but failed to be discovered. Exception: %s' % e)
            return None
    
    def __init__(self, device_directory, device_file):
        self.device_path = os.path.join(device_directory, device_file)
        if not os.path.isfile(self.device_path):
            logging.error('Failed to initialize thermometer at path: %s' % self.device_path)
            raise Exception('No Thermometer device found at path: %s' % self.device_path)

    def read(self):
        try:
            fd = open(self.device_path, 'r')
            slave_data = fd.read()
            if slave_data:
                temp_c = slave_data[slave_data.index('t=') + 2:]
                temp_c = int(temp_c.strip('\n'))
                temp_c = float(temp_c) / 1000
                return temp_c
            else:
                logging.error('Unable to parse temp - fd is None')

        except Exception as e:
            logging.error('Failed to read thermometer file: %s exception: %s' % self.device_path, e)
            return None
