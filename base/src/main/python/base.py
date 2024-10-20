#
# Home Control - Base
# Created by Michael Abood on 10/19/24
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
import datetime
from configparser import ConfigParser
from flask import Flask

app = Flask(__name__)
base_main()

@app.route('/doorbell', methods=['POST'])
def hello_world():
    logging.info('Posted doorbell ring at %s', datetime.datetime.now())
    return "<p>Ring Ring</p>"

def base_main():
    # Resolve homecontrol root directory absolute path
    root_directory = os.getenv(constants.HOMECONTROL_ROOT_ENVIRONMENT_VAR)
    if not root_directory or not os.path.isdir(root_directory):
        print('Unable to resolve homecontrol root directory from environment variables. Use launch.sh to run base')
        sys.exit(1)

    # Setup logging
    log_directory = os.getenv(constants.BASE_RUN_DIR_ENVIRONMENT_VAR)
    if not log_directory or not os.path.isdir(log_directory):
        print('Unable to resolve base run directory from environment variables')
        sys.exit(1)

    # Setup config
    default_config_file = os.path.join(root_directory, constants.BASE_CONFIG_DEFAULT_PATH)
    if not default_config_file or not os.path.isfile(default_config_file):
        print('Failed to resolve base config file at relative path %s' % constants.BASE_CONFIG_DEFAULT_PATH)
        sys.exit(2)
    
    override_config_file = os.path.join(root_directory, constants.BASE_CONFIG_OVERRIDE_PATH)
    if not override_config_file or not os.path.isfile(override_config_file):
        override_config_file = None
            
    try:
        config = ConfigParser()
        config.read(default_config_file)
        if override_config_file is not None:
            config.read(override_config_file)
        utils.setup_logger(constants.BASE_APP_NAME, log_directory, config[constants.CONFIG_SECTION_LOGGING])

        # TODO Integrate base services
        logging.info('No services enabled. Enable services by modifying override config file.')

    except Exception as e:
        logging.error('Base interrupted due to exception: %s', e)
        sys.exit(3)


if __name__ == '__main__':
    base_main()
