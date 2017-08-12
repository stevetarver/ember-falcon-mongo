#!/usr/bin/env bash

# Build docker image

. config.sh

echo "${ECHO_PREFIX} Building '${IMAGE_NAME}'"
docker build -t ${IMAGE_NAME} .

