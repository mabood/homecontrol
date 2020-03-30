#!/bin/bash

# script argument constants
AGENT="agent"
BASE="base"

# Supported OS constants
LINUX="Linux"
MAC="MacOS"

# Repo root directory name
EXPECTED_DIRECTORY="homecontrol"

function print_supported_directives {
    printf "Supported directives:\n"
    printf "   %s\n" ${AGENT} ${BASE}
}

function print_install_banner {
    printf "\n======================================================"
    printf "\n\t\tHome Control Installer"
    printf "\n======================================================"
    printf "\n\nInstalling homecontrol %s for %s \n" "$1" "$2"
}

function print_install_result_and_exit {
    if [ $1 == 0 ]; then
        printf "\nInstallation complete.\n\n"
    else
        printf "\nInstallation failed.\n\n"
    fi
    exit $1
}

function resolve_OS {
    unameOut="$(uname -s)"
    case "${unameOut}" in
        Linux*)     machine=${LINUX};;
        Darwin*)    machine=${MAC};;
        CYGWIN*)    machine=Cygwin;;
        MINGW*)     machine=MinGw;;
        *)          machine="UNKNOWN:${unameOut}"
    esac
    echo "${machine}"
}

function set_environment_vars {
    current_dir=${PWD##*/}
    if [[ "${current_dir}" != ${EXPECTED_DIRECTORY} ]]; then
        printf "\n>\tCurrent directory must be \"%s\" root. cd to that directory to install homecontrol\n" "${EXPECTED_DIRECTORY}";
        return 1
    else
        export HOMECONTROL=$(pwd)
        return 0
    fi
}

function install_agent {
    OS=$1;
    print_install_banner "${AGENT}" "${OS}"

    # Check whether python3 is installed
    if command -v python3 >/dev/null 2>&1; then
        printf "\n>\tpython3 is already installed.\n"
    else
        printf "\n>\tpython3 is not installed. Please install it by running \"$ sudo apt-get install python3.6\"\n"
        print_install_result_and_exit 3
    fi

    # Set environment variables with directory information
    if ! set_environment_vars; then
        print_install_result_and_exit 4;
    fi
    PROTO_SRC=${HOMECONTROL}/protocol/src/main/proto
    PROTO_GEN_PY=${HOMECONTROL}/protocol/build/gen/python
    AGENT_VENV=${HOMECONTROL}/agent/venv

    # install virtualenv
    if ! pip install virtualenv --user; then
        printf "\n>\tvirtualenv installation failed.\n"
        print_install_result_and_exit 5;
    fi

    # create venv
    if [ -d "${AGENT_VENV}" ]; then
        printf "\n>\tvenv directory already exists.\n"
    else
        if ! python -m virtualenv "${AGENT_VENV}" -p python3; then
            printf "\n>\tfailed to create venv directory.\n"
            print_install_result_and_exit 6;
        fi
    fi

    # activate venv
    if ! source "${AGENT_VENV}/bin/activate"; then
        printf "\n>\tfailed to activate venv\n"
        print_install_result_and_exit 7;
    fi

    # install requirements.txt
    if ! pip install -r "${HOMECONTROL}"/agent/requirements.txt; then
        printf "\n>\tfailed to install requirements.txt\n"
        print_install_result_and_exit 8;
    fi

    # codegen python bindings
    printf "\n>\tCompiling gRPC protobuf files...\n"
    GEN_PROTO_GRPC="python -m grpc_tools.protoc --proto_path=${PROTO_SRC} --python_out=${PROTO_GEN_PY} --grpc_python_out=${PROTO_GEN_PY} ${PROTO_SRC}/base/climate.proto"
    if ! ${GEN_PROTO_GRPC}; then
        printf "\n>\tfailed generate grpc protobuf bindings\n"
        print_install_result_and_exit 9;
    fi

    printf "\n>\tAdding generated gRPC python files to path...\n"
    # add generated python files to path
    if ! echo "${PROTO_GEN_PY}" > "${AGENT_VENV}"/lib/python3.6/site-packages/generated-protos.pth; then
        printf "\n>\tfailed generate grpc protobuf bindings\n"
        print_install_result_and_exit 10;
    fi

    print_install_result_and_exit 0
}

function install_base {
    OS=$1;
    print_install_banner "${BASE}" "${OS}"
    print_install_result_and_exit 0
}


#
# Install entry point
#

SYSTEM_OS=$(resolve_OS);

if [ $# != 1 ]; then
    printf "Usage: %s directive\n\n" $0;
    print_supported_directives;
    exit 1;
elif [ "$1" == $AGENT ]; then
    install_agent "${SYSTEM_OS}";
elif [ "$1" == $BASE ]; then
    install_base "${SYSTEM_OS}";
else
    printf "Invalid directive.\n\n";
    print_supported_directives;
    exit 2;
fi

