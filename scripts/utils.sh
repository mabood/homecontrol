#!/bin/bash

# script argument constants
BASE="base"

# Supported OS constants
LINUX="Linux"
MAC="MacOS"

# Name of homecontrol root directory
HOMECONTROL_DIR_NAME="homecontrol"

function set_environment_vars {
    current_dir=${PWD##*/}
    if [[ "${current_dir}" != "${HOMECONTROL_DIR_NAME}" ]]; then
        printf "\n>\tCurrent directory must be \"%s\" root. cd to that directory to use homecontrol scripts\n" "${HOMECONTROL_DIR_NAME}";
        return 1
    else
        export HOMECONTROL=${PWD}
        export RESOURCES_DIR=${HOMECONTROL}/resources
        export BASE_DIR=${HOMECONTROL}/${BASE}
        export VENV_DIR=${HOMECONTROL}/venv
        export REQUIREMENTS_FILE=${HOMECONTROL}/requirements.txt
        export FLASK_APP=${HOMECONTROL}/src/main/python/app.py
        export BASE_RUN_DIR=${BASE_DIR}/run
        export BASE_CONF_DIR=${BASE_DIR}/conf
        export BASE_CONF_OVERRIDE_FILE=${BASE_CONF_DIR}/${BASE}-override.conf

        return 0
    fi
}

function activate_venv {
    if ! source "${VENV_DIR}/bin/activate"; then
        printf "\n>\tfailed to activate venv.\n"
        exit 5
    fi
    return 0
}