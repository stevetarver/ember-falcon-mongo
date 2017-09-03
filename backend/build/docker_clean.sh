#!/usr/bin/env bash
#
# Remove docker images produced during build
#

ECHO_PREFIX='===>'
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. ${SCRIPT_DIR}/config.sh


# Delete any existing images
if [[ "$(docker images -q ${DOCKER_IMAGE_NAMETAG} 2> /dev/null)" != "" ]]; then
    echo "$ECHO_PREFIX Removing '${DOCKER_IMAGE_NAMETAG}' image"
    docker rmi -f ${DOCKER_IMAGE_NAMETAG}
else
    echo "$ECHO_PREFIX '${DOCKER_IMAGE_NAMETAG}' image does not exist"
fi

# Delete any orphaned (dangling) images
if [[ "$(docker images -q -f dangling=true 2> /dev/null)" != "" ]]; then
    echo "$ECHO_PREFIX Removing dangling images"
    docker rmi -f $(docker images -q -f dangling=true)
fi
