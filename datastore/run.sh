#!/usr/bin/env bash

# Create/start a new container from the existing image

. config.sh

# NOTE: Data is inserted into the 'test' database by default. You can change the target db by
#       adding MONGO_INITDB_DATABASE env var to the run command:
#       -e MONGO_INITDB_DATABASE=application

echo "${ECHO_PREFIX} Creating and starting '${CONTAINER_NAME}'"
docker run --name ${CONTAINER_NAME} \
    -p 27017:27017                  \
    --restart=always                \
    -d ${IMAGE_NAME}
