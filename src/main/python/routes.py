#
# Home Control - Routes
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

import os
import logging
import datetime
import constants
import json
from flask import Blueprint, jsonify
from services import Chime
from app import Base

route_blueprint = Blueprint('route_blueprint', __name__)

@route_blueprint.route('/doorbell')
def doorbell():
    logging.info('Received doorbell ring at %s', datetime.datetime.now())
    chime = Base().doorbell_chime
    if chime is not None:
        chime.ring()
        return "<p>Ring Ring</p>"
    else:
        return "<p>No Chime Configured</p>"

@route_blueprint.route('/switchbot/<name>/<action>', methods=['POST'])
def operate_switch(name, action):  # <-- Removed 'async'
    try:
        # Standard function call
        mac_address = Base().switchbot_controller.operate_switchbot(name, action) # <-- Removed 'await'
        
        return jsonify({
            "status": "success",
            "device": name,
            "mac": mac_address,
            "action": action
        }), 200

    except KeyError as ke:
        return jsonify({"error": str(ke).strip("'")}), 404
        
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
