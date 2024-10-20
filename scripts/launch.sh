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

function launch {
    export APP_NAME=$0
    export RUN_DIR=$1
    export CONFIG_DIR=$2

    RUN_PID_FILE="${RUN_DIR}/pid"

    if ! [ -d "${VENV_DIR:?}" ]; then
        printf "Virtual environment not found. Run the install script before launching."
        exit 4
    fi

    if ! mkdir -p "${RUN_DIR:?}"; then
        printf "Failed to create run directory"
        exit 5
    fi

    # Check if agent is already running
    if [ -f "${RUN_PID_FILE:?}" ]; then
        if ps aux | grep -f "${RUN_PID_FILE:?}"; then
            printf "Home Control ${APP_NAME} already running on pid=%s\n" "$(cat "${RUN_PID_FILE:?}")"
            exit 0
        fi
    fi

    printf "Launching Home Control ${APP_NAME}...\n"
    activate_venv;
    nohup flask --app "${FLASK_APP:?}" run --host=0.0.0.0 >"${RUN_DIR:?}"/"${APP_NAME:?}"-launch.log 2>&1 & echo $! > "${RUN_PID_FILE:?}"
}

# Set environment variables
if ! set_environment_vars; then
    exit 3;
fi

if [ $# != 1 ]; then
    printf "Usage: %s directive\n\n" $0;
    print_supported_directives;
    exit 1;
elif [ "$1" == "$AGENT" ]; then
    launch $1 "${AGENT_RUN_DIR:?}" "${AGENT_CONF_DIR:?}";
elif [ "$1" == "$BASE" ]; then
    launch $1 "${BASE_RUN_DIR:?}" "${BASE_CONF_DIR:?}";
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi

