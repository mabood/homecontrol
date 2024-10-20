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

function kill {
    APP_NAME=$0
    RUN_DIR=$1
    RUN_PID_FILE="${RUN_DIR}/pid"

    # Kill if already running
    if [ -f "${RUN_PID_FILE:?}" ]; then
        if ps aux | grep -f "${RUN_PID_FILE:?}"; then
            PID=$(<"${RUN_PID_FILE:?}")
            if ! kill -9 "$PID"; then
                printf "\n>\tFailed to kill running ${APP_NAME} with pid %s\n" "$PID";
                exit 2
            else
                printf "\n>\t${APP_NAME} with pid %s killed.\n" "$PID";
            fi
        else
            printf "\n>\t${APP_NAME} not running.\n";
        fi
    else
        printf "\n>\t${APP_NAME} not running.\n";
    fi

    exit 0
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
    kill $1 "${AGENT_RUN_DIR:?}";
elif [ "$1" == "$BASE" ]; then
    kill $1 "${BASE_RUN_DIR:?}";
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi
