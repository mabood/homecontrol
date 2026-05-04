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
    export APP_NAME='base'
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

    printf "Launching Home Control base...\n"
    activate_venv;
    # Launch the server in the background and capture the PID
    nohup flask --app "${FLASK_APP:?}" run --host=0.0.0.0 >"${RUN_DIR:?}"/launch.log 2>&1 & echo $! > "${RUN_PID_FILE:?}"
}

# Set environment variables
if ! set_environment_vars; then
    exit 3;
fi

if [ $# != 0 ]; then
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
else
    launch "${BASE_RUN_DIR:?}" "${BASE_CONF_DIR:?}";
fi

