#!/usr/bin/env bash

# Build the docker image

ECHO_PREFIX='===>'
OPERATION=$1
CONTAINER_NAME=cloud-starter-falcon
IMAGE_NAME=cloud-starter-falcon
BUILD_CMD="docker build -t $IMAGE_NAME ."
RUN_CMD="docker run --name $CONTAINER_NAME
            -p 8000:8000
            --restart=always
            -e MONGO_URI='mongodb://192.168.86.21:27017/'
            -d $IMAGE_NAME"

showHelp() {
    echo "Use: ./build.sh CMD"
    echo "    CMD    = build | run | teardown"
}

# Arg validation
if [[ ( $OPERATION != "build" &&  $OPERATION != "run" &&  $OPERATION != "teardown") ]]; then
    showHelp
    exit 1
fi

case $OPERATION in
    build)
        echo "$ECHO_PREFIX Building docker image $IMAGE_NAME"
        eval $BUILD_CMD
        ;;

    run)
        echo "$ECHO_PREFIX Creating and starting '$CONTAINER_NAME'"
        echo $RUN_CMD
        eval $RUN_CMD
        ;;

    teardown)
        # Stop any existing containers
        RUNNING=$(docker inspect --format="{{ .State.Running }}" $CONTAINER_NAME 2> /dev/null)

        if [ "$RUNNING" == "true" ]; then
            echo "$ECHO_PREFIX Stopping '$CONTAINER_NAME' container"
            docker stop $CONTAINER_NAME
        else
            echo "$ECHO_PREFIX '$CONTAINER_NAME' container is not running"
        fi

        # Delete any existing containers and volumes
        if [[ "$(docker ps -aq --filter name=$CONTAINER_NAME 2> /dev/null)" != "" ]]; then
            echo "$ECHO_PREFIX Removing '$CONTAINER_NAME' container"
            docker rm -v $CONTAINER_NAME
        else
            echo "$ECHO_PREFIX '$CONTAINER_NAME' container does not exist"
        fi

        # Delete any existing images
        if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" != "" ]]; then
            echo "$ECHO_PREFIX Removing '$IMAGE_NAME' image"
            docker rmi -f $IMAGE_NAME
        else
            echo "$ECHO_PREFIX '$IMAGE_NAME' image does not exist"
        fi

        # Delete any orphaned (dangling) images
        if [[ "$(docker images -q -f dangling=true 2> /dev/null)" != "" ]]; then
            echo "$ECHO_PREFIX Removing dangling images"
            docker rmi -f $(docker images -q -f dangling=true)
        fi
        ;;
esac

