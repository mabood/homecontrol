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

import logging
import constants
import sensors
import grpc
import climate_pb2 as climate
import climate_pb2_grpc as climate_grpc
from threading import Timer
from google.protobuf.timestamp_pb2 import Timestamp

CONFIG_KEY_ADDRESS = 'address'
CONFIG_KEY_GRPC_PORT = 'grpc_port'
CONFIG_KEY_CLIMATE_ENABLED = 'climate_enabled'

class ServiceManager(object):
    def __init__(self, config):
        self.config = config
        services_config = config[constants.AGENT_CONFIG_SECTION_SERVICES]
        self.has_services = False
        self.has_climate = eval(services_config[CONFIG_KEY_CLIMATE_ENABLED])
        self.has_services = self.has_climate

        if self.has_services:
            self.channel = self.initialize_grpc_channel()

        if self.has_climate:
            logging.info('Climate service enabled in configs.')
            self.climate = ClimateClient(self.channel, self.config)

    def initialize_grpc_channel(self):
        base_host_address = self.config.get(constants.AGENT_CONFIG_SECTION_BASE_SERVER, CONFIG_KEY_ADDRESS)
        if base_host_address is None:
            logging.error('Failed to resolve base host from agent config.')
            raise Exception('Base host address not found')

        base_host_grpc_port = self.config.get(constants.AGENT_CONFIG_SECTION_BASE_SERVER, CONFIG_KEY_GRPC_PORT)
        if base_host_grpc_port is None:
            logging.error('Failed to resolve base host gRPC port from agent config.')
            raise Exception('Base host gRPC port not found')

        base_channel = grpc.insecure_channel(base_host_address + ':' + base_host_grpc_port)
        logging.info(
            'gRPC channel initialized using address: %s and port %s' % (base_host_address, base_host_grpc_port))
        return base_channel

    def start_services(self):
        if self.has_services:
            logging.info('Starting Services...')
            if self.has_climate:
                self.climate.start()

        else:
            logging.info('No services enabled. Enable services by modifying override config file.')


CONFIG_KEY_CLIMATE_POLL_INTERVAL = 'climate_poll_interval_seconds'


class ClimateClient(object):
    def __init__(self, server_grpc_channel, config):
        self.config = config
        self.channel = server_grpc_channel
        self.thermometer = sensors.Thermometer.make(config[constants.AGENT_CONFIG_SECTION_SENSORS])
        self.interval_timer = None

    def start(self):
        timestamp = Timestamp()

        # Check prerequisites
        if self.thermometer is None:
            logging.error('Failed to start Climate Client - thermometer is not setup. Check logs for exception.')
            return

        # Schedule interval job
        poll_interval = self.config.get(constants.AGENT_CONFIG_SECTION_SERVICES, CONFIG_KEY_CLIMATE_POLL_INTERVAL)
        logging.info('Begin polling thermometer on interval of %s seconds' % poll_interval)
        self.interval_timer = IntervalTimer(float(poll_interval), self.report_temp)
        self.interval_timer.start()
        
    def stop(self):
        if self.interval_timer is not None:
            self.interval_timer.stop()

    def report_temp(self):
        thermometer_value = self.thermometer.read()
        if thermometer_value is None:
            logging.error('Failed to read thermal sensor. stopping interval execution.')
            self.interval_timer.stop()
            return
        logging.debug('read thermometer value (celsius): %s' % thermometer_value)


class IntervalTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False