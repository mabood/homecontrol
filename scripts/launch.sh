#!/bin/bash

# Ensure that we are in the root directory and source utils.sh
readonly ROOT_DIR_NAME='homecontrol'
current_dir=${PWD##*/}
if [[ "${current_dir}" != "${ROOT_DIR_NAME}" ]]; then
    printf "\n>\tCurrent directory must be \"%s\" root. cd to that directory to install homecontrol\n" "${ROOT_DIR_NAME}";
    exit 1
fi
readonly UTILS=$(pwd)/scripts/utils.sh
# shellcheck disable=SC1090
source "${UTILS}"

function launch_agent {

    # Set environment variables
    if ! set_environment_vars; then
        exit 3;
    fi

    if ! [ -d "${VENV_DIR:?}" ]; then
        printf "Virtual environment not found. Run the install script before launching."
        exit 4
    fi

    if ! mkdir -p "${AGENT_RUN_DIR:?}"; then
        printf "Failed to create agent run directory"
        exit 5
    fi

    # Check if agent is already running
    if [ -f "${AGENT_RUN_PID_FILE:?}" ]; then
        if ps aux | grep -f "${AGENT_RUN_PID_FILE:?}"; then
            printf "Home Control Agent already running on pid=%s\n" "$(cat "${AGENT_RUN_PID_FILE:?}")"
            exit 0
        fi
    fi

    printf "Launching Home Control Agent...\n"
    activate_venv;
    nohup python "${AGENT_DIR:?}"/src/main/python/agent.py >"${AGENT_RUN_DIR:?}"/"${AGENT:?}"-launch.log 2>&1 & echo $! > "${AGENT_RUN_PID_FILE:?}"
}

function launch_base {

    # Set environment variables
    if ! set_environment_vars; then
        exit 3;
    fi

    if ! [ -d "${VENV_DIR:?}" ]; then
        printf "Virtual environment not found. Run the install script before launching."
        exit 4
    fi

    if ! mkdir -p "${BASE_RUN_DIR:?}"; then
        printf "Failed to create base run directory"
        exit 5
    fi

    # Check if agent is already running
    if [ -f "${BASE_RUN_PID_FILE:?}" ]; then
        if ps aux | grep -f "${BASE_RUN_PID_FILE:?}"; then
            printf "Home Control Base already running on pid=%s\n" "$(cat "${BASE_RUN_PID_FILE:?}")"
            exit 0
        fi
    fi

    printf "Launching Home Control Base...\n"
    activate_venv;
    nohup python "${BASE_DIR:?}"/src/main/python/base.py >"${BASE_RUN_DIR:?}"/"${BASE:?}"-launch.log 2>&1 & echo $! > "${BASE_RUN_PID_FILE:?}"
}


if [ $# != 1 ]; then
    printf "Usage: %s directive\n\n" $0;
    print_supported_directives;
    exit 1;
elif [ "$1" == "$AGENT" ]; then
    launch_agent;
elif [ "$1" == "$BASE" ]; then
    launch_base;
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi

