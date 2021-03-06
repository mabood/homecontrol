#
# Home Control - Agent
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

import sys
import os
import logging
import utils
import constants
from services import ServiceManager
from configparser import ConfigParser


def agent_main():
    # Resolve homecontrol root directory absolute path
    root_directory = os.getenv(constants.HOMECONTROL_ROOT_ENVIRONMENT_VAR)
    if not root_directory or not os.path.isdir(root_directory):
        print('Unable to resolve homecontrol root directory from environment variables. Use launch.sh to run agent')
        sys.exit(1)

    # Setup logging
    log_directory = os.getenv(constants.AGENT_RUN_DIR_ENVIRONMENT_VAR)
    if not log_directory or not os.path.isdir(log_directory):
        print('Unable to resolve agent run directory from environment variables')
        sys.exit(1)

    # Setup config
    default_config_file = os.path.join(root_directory, constants.AGENT_CONFIG_DEFAULT_PATH)
    if not default_config_file or not os.path.isfile(default_config_file):
        print('Failed to resolve agent config file at relative path %s' % constants.AGENT_CONFIG_PATH)
        sys.exit(2)
    
    override_config_file = os.path.join(root_directory, constants.AGENT_CONFIG_OVERRIDE_PATH)
    if not override_config_file or not os.path.isfile(override_config_file):
        override_config_file = None
            
    try:
        config = ConfigParser()
        config.read(default_config_file)
        if override_config_file is not None:
            config.read(override_config_file)
        utils.setup_logger(constants.AGENT_APP_NAME, log_directory, config[constants.AGENT_CONFIG_SECTION_LOGGING])

        # Start agent services
        services = ServiceManager(config)
        services.start_services()
    except Exception as e:
        logging.error('Agent interrupted due to exception: %s', e)
        sys.exit(3)


if __name__ == '__main__':
    agent_main()
