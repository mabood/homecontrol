#!/bin/bash

# script argument constants
AGENT="agent"
BASE="base"

# Supported OS constants
LINUX="Linux"
MAC="MacOS"

# Name of homecontrol root directory
HOMECONTROL_DIR_NAME="homecontrol"

function print_supported_directives {
    printf "Supported directives:\n"
    printf "   %s\n" ${AGENT} ${BASE}
}

function set_environment_vars {
    current_dir=${PWD##*/}
    if [[ "${current_dir}" != "${HOMECONTROL_DIR_NAME}" ]]; then
        printf "\n>\tCurrent directory must be \"%s\" root. cd to that directory to use homecontrol scripts\n" "${HOMECONTROL_DIR_NAME}";
        return 1
    else
        export HOMECONTROL=${PWD}
        export AGENT_DIR=${HOMECONTROL}/agent
        export BASE_DIR=${HOMECONTROL}/base
        export VENV_DIR=${HOMECONTROL}/venv
        export REQUIREMENTS_FILE=${HOMECONTROL}/requirements.txt
        export FLASK_APP=${HOMECONTROL}/src/main/python/app.py
        export PROTO_SRC_DIR=${HOMECONTROL}/src/main/proto
        export PROTO_GEN_PYTHON_DIR=${HOMECONTROL}/build/gen/python
        export AGENT_RUN_DIR=${AGENT_DIR}/run
        export AGENT_CONF_DIR=${AGENT_DIR}/conf
        export BASE_RUN_DIR=${BASE_DIR}/run
        export BASE_CONF_DIR=${BASE_DIR}/conf

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