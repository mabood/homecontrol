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

function kill_agent {

    # Set environment variables
    if ! set_environment_vars; then
        exit 3;
    fi

    # Kill agent if already running
    if [ -f "${AGENT_RUN_PID_FILE:?}" ]; then
        if ps aux | grep -f "${AGENT_RUN_PID_FILE:?}"; then
            AGENT_PID=$(<"${AGENT_RUN_PID_FILE:?}")
            if ! kill -9 "$AGENT_PID"; then
                printf "\n>\tFailed to kill running agent with pid %s\n" "$AGENT_PID";
                exit 2
            else
                printf "\n>\tAgent with pid %s killed.\n" "$AGENT_PID";
            fi
        else
            printf "\n>\tAgent not running.\n";
        fi
    else
        printf "\n>\tAgent not running.\n";
    fi

    exit 0
}

function kill_base {

    # Set environment variables
    if ! set_environment_vars; then
        exit 3;
    fi

    # Kill base if already running
    if [ -f "${BASE_RUN_PID_FILE:?}" ]; then
        if ps aux | grep -f "${BASE_RUN_PID_FILE:?}"; then
            BASE_PID=$(<"${BASE_RUN_PID_FILE:?}")
            if ! kill -9 "$BASE_PID"; then
                printf "\n>\tFailed to kill running base with pid %s\n" "$BASE_PID";
                exit 2
            else
                printf "\n>\Base with pid %s killed.\n" "$BASE_PID";
            fi
        else
            printf "\n>\Base not running.\n";
        fi
    else
        printf "\n>\Base not running.\n";
    fi

    exit 0
}


if [ $# != 1 ]; then
    printf "Usage: %s directive\n\n" $0;
    print_supported_directives;
    exit 1;
elif [ "$1" == "$AGENT" ]; then
    kill_agent;
elif [ "$1" == "$BASE" ]; then
    kill_base;
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi
