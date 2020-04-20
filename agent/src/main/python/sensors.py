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
import constants
import os


class SensorManager(object):
    def __init__(self, config):
        sensors_config = config[constants.AGENT_CONFIG_SECTION_SENSORS]
        self.hasThermometer = eval(sensors_config[constants.AGENT_CONFIG_KEY_THERMOMETER])
        if self.hasThermometer:
            try:
                self.thermometer = Thermometer(sensors_config[constants.AGENT_CONFIG_KEY_THERMOMETER_DIR],
                                               sensors_config[constants.AGENT_CONFIG_KEY_THERMOMETER_FILE])
            except Exception as e:
                logging.error('Thermometer is enabled in configs, but failed to be discovered. Exception: %s' % e)
                raise Exception(e)

    def start_collection(self):
        logging.info('Starting sensor data collection...')
        if self.hasThermometer:
            logging.info('Reading thermometer at path: %s' % self.thermometer.device_path)


class Thermometer(object):
    def __init__(self, device_directory, device_file):
        self.device_path = os.path.join(device_directory, device_file)
        if not os.path.isfile(self.device_path):
            logging.error('Failed to initialize thermometer at path: %s' % self.device_path)
            raise Exception('No Thermometer device found at path: %s' % self.device_path)
