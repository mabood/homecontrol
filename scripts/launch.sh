#!/bin/bash

# Ensure that we are in the root directory and source utils.sh
readonly ROOT_DIR_NAME='homecontrol'
current_dir=${PWD##*/}
if [[ "${current_dir}" != "${ROOT_DIR_NAME}" ]]; then
    printf "\n>\tCurrent directory must be \"%s\" root. cd to that directory to install homecontrol\n" "${ROOT_DIR_NAME}";
    exit 1
fi
readonly UTILS=$(pwd)/scripts/utils.sh
source "${UTILS}"

function launch_agent {

    # Set environment variables
    if ! set_environment_vars; then
        exit 3;
    fi

    if ! [ -d "${AGENT_VENV}" ]; then
        printf "Agent virtual environment not found. Run the install script before launching."
        exit 4
    fi

    if ! mkdir -p "${AGENT_RUN_DIR}"; then
        printf "Failed to create run directory"
        exit 5
    fi

    # Check if agent is already running
    if [ -f "${AGENT_RUN_PID_FILE}" ]; then
        if ps aux | grep -f "${AGENT_RUN_PID_FILE}"; then
            printf "Home Control Agent already running on pid=%s\n" $(cat "${AGENT_RUN_PID_FILE}")
            exit 0
        fi
    fi

    printf "Launching Home Control Agent...\n"
    activate_venv;
    nohup python "${AGENT_DIR}"/src/main/python/agent.py >"${AGENT_RUN_DIR}"/"${AGENT}"-launch.log 2>&1 & echo $! > "${AGENT_RUN_PID_FILE}"
}

function launch_base {
    printf "Launching Home Control Base..."

    exit 0
}


if [ $# != 1 ]; then
    printf "Usage: %s directive\n\n" $0;
    print_supported_directives;
    exit 1;
elif [ "$1" == $AGENT ]; then
    launch_agent;
elif [ "$1" == $BASE ]; then
    launch_base;
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi

