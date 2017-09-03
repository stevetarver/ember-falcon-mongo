#!/usr/bin/env bash
#
# Bring down the environment via docker-compose
#
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. ${SCRIPT_DIR}/config.sh

(
    cd ${SCRIPT_DIR}

    docker-compose down
)

