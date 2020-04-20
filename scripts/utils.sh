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
        export AGENT_VENV=${AGENT_DIR}/venv
        export PROTOCOL_DIR=${HOMECONTROL}/protocol
        export PROTO_SRC_DIR=${PROTOCOL_DIR}/src/main/proto
        export PROTO_GEN_PYTHON_DIR=${PROTOCOL_DIR}/build/gen/python
        export CORE_DIR=${HOMECONTROL}/core
        export CORE_SRC_DIR=${CORE_DIR}/src/main/python
        export AGENT_RUN_DIR=${AGENT_DIR}/run
        export AGENT_RUN_PID_FILE="${AGENT_RUN_DIR}/pid"

        return 0
    fi
}

function activate_venv {
    if ! source "${AGENT_VENV}/bin/activate"; then
        printf "\n>\tfailed to activate venv.\n"
        exit 5
    fi
    return 0
}