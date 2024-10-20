#
# Home Control - App
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
from flask import Flask

def create_app():
    setup()

    app = Flask(__name__)

    from routes import route_blueprint
    app.register_blueprint(route_blueprint)

    return app

def setup():
    # Resolve homecontrol root directory absolute path
    root_directory = os.getenv(constants.HOMECONTROL_ROOT_ENV)
    if not root_directory or not os.path.isdir(root_directory):
        print('Unable to resolve homecontrol root directory from environment variables. Use launch.sh to run application')
        sys.exit(1)

    # Resolve app name
    app_name = os.getenv(constants.APP_NAME_ENV)
    if app_name is None:
        print('Unable to resolve app name from environment variables. Use launch.sh to run application')
        sys.exit(1)

    # Resolve run dir
    log_directory = os.getenv(constants.RUN_DIR_ENV)
    if not log_directory or not os.path.isdir(log_directory):
        print('Unable to resolve run directory from environment variables')
        sys.exit(1)

    # Resolve config dir
    config_directory = os.getenv(constants.CONFIG_DIR_ENV)
    if not config_directory or not os.path.isdir(config_directory):
        print('Unable to resolve config directory from environment variables')
        sys.exit(1)

    # Resolve default config file
    default_config_file = os.path.join(config_directory, ('%s-default.conf' % app_name))
    if not default_config_file or not os.path.isfile(default_config_file):
        print('Failed to resolve default config file at path %s' % default_config_file)
        sys.exit(2)
    
    # Resolve override config file
    override_config_file = os.path.join(config_directory, ('%s-override.conf' % app_name))
    if not override_config_file or not os.path.isfile(override_config_file):
        override_config_file = None
            
    try:
        config = ConfigParser()
        config.read(default_config_file)
        if override_config_file is not None:
            config.read(override_config_file)
        utils.setup_logger(app_name, log_directory, config[constants.CONFIG_SECTION_LOGGING])

        # Start agent services
        services = ServiceManager(config)
        services.start_services()
    except Exception as e:
        logging.error('%s interrupted due to exception: %s', app_name, e)
        sys.exit(3)


