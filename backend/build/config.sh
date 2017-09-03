#!/bin/sh
#
# Provide config for other scripts, including version information
#
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. ${SCRIPT_DIR}/version.sh

export REPO_NAME=$(git config remote.origin.url | cut -d '/' -f5 | cut -d '.' -f1)
export SERVICE_TYPE='demo'
export SERVICE_NAME='backend-falcon'

export DOCKER_REGISTRY='docker.io'
export DOCKER_GROUP='makara'
export DOCKER_VERSION="${MAJOR_VER}.${MINOR_VER}.${MICRO_VER}"
export DOCKER_IMAGE_NAME="${DOCKER_REGISTRY}/${DOCKER_GROUP}/${SERVICE_NAME}"
export DOCKER_IMAGE_NAMETAG="${DOCKER_IMAGE_NAME}:${DOCKER_VERSION}"
