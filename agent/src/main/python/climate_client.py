#
# Home Control - Climate Client
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
import climate_pb2 as climate
import climate_pb2_grpc as climate_grpc
from google.protobuf.timestamp_pb2 import Timestamp


class ClimateClient(object):
    def __init__(self, server_grpc_channel):
        self.channel = server_grpc_channel

    def run(self):
        logging.info("Starting climate client...")
        timestamp = Timestamp()
