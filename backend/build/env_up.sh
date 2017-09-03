#!/usr/bin/env bash
#
# Start the service and datastore containers through docker-compose
#
# Example mongo docker start command
#    docker run --name $CONTAINER_NAME   \
#        -p 27017:27017                  \
#        --restart=always                \
#        -d $IMAGE_NAME
#
# Example falcon docker start command
#    docker run --name $CONTAINER_NAME \
#                -p 8000:8000          \
#                --restart=always      \
#                -e MONGO_URI='mongodb://192.168.86.21:27017/' \
#                -d $IMAGE_NAME
#
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

. ${SCRIPT_DIR}/config.sh

(
    cd ${SCRIPT_DIR}

    docker-compose up -d
)