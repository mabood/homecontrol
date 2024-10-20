#
# Home Control - Utils
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
from logging.handlers import RotatingFileHandler
import os

CONFIG_KEY_LOG_VERBOSE = 'log_verbose'
CONFIG_KEY_LOG_TO_CONSOLE = 'log_to_console'
CONFIG_KEY_LOG_FILE_LIMIT = 'log_file_size_limit_bytes'


def setup_logger(app_name, log_dir, logging_config):    
    if not app_name:
        raise Exception('cannot create logger with app_name=None')

    if not log_dir:
        raise Exception('cannot create logger with log_dir=None')

    if not os.path.isdir(log_dir):
        os.makedirs(log_dir)
    
    log_to_console = eval(logging_config[CONFIG_KEY_LOG_TO_CONSOLE])
    verbose = eval(logging_config[CONFIG_KEY_LOG_VERBOSE])
    log_file_limit = int(logging_config[CONFIG_KEY_LOG_FILE_LIMIT])

    log_file_name = app_name + '.log'
    log_path = os.path.join(log_dir, log_file_name)
    log_format = app_name + ' [%(levelname)s] %(asctime)s, %(message)s'

    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level,
                        format=log_format,
                        datefmt='%Y-%m-%d-%H:%M:%S',
                        filename=log_path,
                        filemode='w+')
    log = logging.getLogger('root')
    handler = RotatingFileHandler(log_path, maxBytes=log_file_limit, backupCount=1)
    log.addHandler(handler)

    if log_to_console:
        console = logging.StreamHandler()
        formatter = logging.Formatter(log_format, '%Y-%m-%d-%H:%M:%S')
        console.setFormatter(formatter)
        console.setLevel(log_level)
        logging.getLogger('').addHandler(console)

