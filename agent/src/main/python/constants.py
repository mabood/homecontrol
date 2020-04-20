#
# Home Control - Agent Constants
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


# Environment variable constants
HOMECONTROL_ROOT_ENVIRONMENT_VAR = 'HOMECONTROL'
AGENT_RUN_DIR_ENVIRONMENT_VAR = 'AGENT_RUN_DIR'

# Agent properties
AGENT_APP_NAME = 'homecontrol-agent'

# Agent config
AGENT_CONFIG_PATH = 'agent/conf/agent-default.conf'

# Agent config sections
AGENT_CONFIG_SECTION_BASE_SERVER = 'BASE_SERVER'
AGENT_CONFIG_SECTION_SERVICES = 'SERVICES'
AGENT_CONFIG_SECTION_SENSORS = 'SENSORS'

# Agent config keys
AGENT_CONFIG_KEY_ADDRESS = 'address'
AGENT_CONFIG_KEY_GRPC_PORT = 'grpc_port'
AGENT_CONFIG_KEY_CLIMATE = 'climate'
AGENT_CONFIG_KEY_THERMOMETER = 'thermometer'
AGENT_CONFIG_KEY_THERMOMETER_DIR = 'thermometer_device_dir'
AGENT_CONFIG_KEY_THERMOMETER_FILE = 'thermometer_device_file'
