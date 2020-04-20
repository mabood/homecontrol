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
import grpc
import climate_pb2 as climate
import climate_pb2_grpc as climate_grpc
from google.protobuf.timestamp_pb2 import Timestamp


class ServiceManager(object):
    def __init__(self, config):
        self.config = config
        services_config = config[constants.AGENT_CONFIG_SECTION_SERVICES]
        self.has_services = False
        self.has_climate = eval(services_config[constants.AGENT_CONFIG_KEY_CLIMATE])
        self.has_services = self.has_climate

        if self.has_services:
            self.channel = self.initialize_grpc_channel()

        if self.has_climate:
            logging.info('Climate service enabled in configs.')
            self.climate = ClimateClient(self.channel)

    def initialize_grpc_channel(self):
        base_host_address = self.config.get(constants.AGENT_CONFIG_SECTION_BASE_SERVER,
                                            constants.AGENT_CONFIG_KEY_ADDRESS)
        if base_host_address is None:
            logging.error('Failed to resolve base host from agent config.')
            raise Exception('Base host address not found')

        base_host_grpc_port = self.config.get(constants.AGENT_CONFIG_SECTION_BASE_SERVER,
                                              constants.AGENT_CONFIG_KEY_GRPC_PORT)
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
            logging.info('No services enabled.')


class ClimateClient(object):
    def __init__(self, server_grpc_channel):
        self.channel = server_grpc_channel

    def start(self):
        timestamp = Timestamp()
        logging.info('Starting Climate service client...')
