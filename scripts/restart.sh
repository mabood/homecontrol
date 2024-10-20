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

function restart {

    # Kill if already running
    if ! $(pwd)/scripts/kill.sh "$0"; then
        printf "\n>\tFailed to kill running $0.\n"
        exit 4
    fi

    if ! $(pwd)/scripts/launch.sh "$0"; then
        printf "\n>\tFailed to launch $0.\n"
        exit 5
    fi

    exit 0
}

function restart_base {

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
    restart $1;
elif [ "$1" == "$BASE" ]; then
    restart $1;
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi

