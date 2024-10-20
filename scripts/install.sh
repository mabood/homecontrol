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

function print_install_banner {
    printf "\n======================================================"
    printf "\n\t\tHome Control Installer"
    printf "\n======================================================"
    printf "\n\nInstalling homecontrol for %s \n" "$1"
}

function print_install_result_and_exit {
    if [ "$1" == 0 ]; then
        printf "\nInstallation complete!\n\n"
    else
        printf "\nInstallation failed.\n\n"
    fi
    exit "$1"
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



function install {
    OS=$0;
    print_install_banner "${OS}"

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

    # create venv
    if [ -d "${VENV_DIR}" ]; then
        printf "\n>\tvenv directory already exists.\n"
    else
        if ! python3 -m venv "${VENV_DIR:?}"; then
            printf "\n>\tfailed to create venv directory.\n"
            print_install_result_and_exit 6;
        fi
    fi

    # activate venv
    printf "\n>\tActivating venv...\n"

    activate_venv;

    printf "\n>\tInstalling requirements.txt...\n"
    # install requirements.txt
    if ! pip install -r "${REQUIREMENTS_FILE:?}"; then
        printf "\n>\tfailed to install requirements.txt\n"
        print_install_result_and_exit 8;
    fi

    # codegen python bindings
    if ! mkdir -p "${PROTO_GEN_PYTHON_DIR:?}"; then
        printf "\n>\tFailed to create gRPC codegen directory at %s\n" "${PROTO_GEN_PYTHON_DIR:?}"
        print_install_result_and_exit 9;
    fi

    printf "\n>\tCompiling gRPC protobuf files...\n"
    if ! rm -rf "${PROTO_GEN_PYTHON_DIR:?}/*"; then
        printf "\n>\tfailed clean python protobuf output directory\n"
        print_install_result_and_exit 10;
    fi

    GEN_PROTO_GRPC="python -m grpc_tools.protoc --proto_path=${PROTO_SRC_DIR:?} --python_out=${PROTO_GEN_PYTHON_DIR:?} --grpc_python_out=${PROTO_GEN_PYTHON_DIR:?} ${PROTO_SRC_DIR:?}/climate.proto"
    if ! ${GEN_PROTO_GRPC}; then
        printf "\n>\tfailed generate grpc protobuf bindings\n"
        print_install_result_and_exit 10;
    fi

    printf "\n>\tAdding generated gRPC python files to path...\n"
    VENV_DIR_PYTHON_DIR=$(find "${VENV_DIR:?}"/lib -maxdepth 1 -name "python*")
    if [ -z "${VENV_DIR_PYTHON_DIR}" ]; then
        printf "\n>\tCannot locate python3.X directory in venv.\n"
        print_install_result_and_exit 11;
    fi

    # add generated python files to path
    if ! echo "${PROTO_GEN_PYTHON_DIR:?}" > "${VENV_DIR_PYTHON_DIR:?}"/site-packages/generated-protos.pth; then
        printf "\n>\tFailed to add generated python files to venv path.\n"
        print_install_result_and_exit 12;
    fi

    printf "\n>\tCreating agent config override file...\n"
    # create agent config override file
    if ! [ -f "${AGENT_CONF_OVERRIDE_FILE}" ]; then
        printf "# Edit this file to override default configs for agent\n\n[LOGGING]\nlog_verbose=1\n" > "${AGENT_CONF_OVERRIDE_FILE}";
    else
        printf "\n>\tAgent config override file already exists.\n"
    fi

    printf "\n>\tCreating base config override file...\n"
    # create base config override file
    if ! [ -f "${BASE_CONF_OVERRIDE_FILE}" ]; then
        printf "# Edit this file to override default configs for base\n\n[LOGGING]\nlog_verbose=1\n" > "${BASE_CONF_OVERRIDE_FILE}";
    else
        printf "\n>\tBase config override file already exists.\n"
    fi

    print_install_result_and_exit 0
}

#
# Install entry point
#

SYSTEM_OS=$(resolve_OS);

install "${SYSTEM_OS:?}";

