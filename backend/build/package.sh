#!/usr/bin/env bash
#
# Package the app - build the docker image, etc.
#
# return: non-zero on any error
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. ${SCRIPT_DIR}/config.sh
. ${SCRIPT_DIR}/common.sh

# Generate fresh build info
${SCRIPT_DIR}/generate_build_info.sh

if [[ $? -ne 0 ]]; then
    fatal "generate_build_info.sh failed"
fi

# Ensure we are in the proper directory for a docker build
(
    cd ${SCRIPT_DIR}/..
    docker build \
        -f build/Dockerfile \
        -t ${DOCKER_IMAGE_NAMETAG} \
        .
)