#!/bin/bash

# Constants
CONTAINER_NAME="room-listing-service-sqoin-sqoin"
PORT="5010"
IMAGE_ID="bb6e8909-a66e-44a5-a007-fb79180be3fa"

# Check if a container with the same name already exists
existing_container=$(docker ps -aq -f name=^$CONTAINER_NAME$)
if [ ! -z "$existing_container" ]; then
    echo "Container with name $CONTAINER_NAME already exists, removing..."
    docker rm -f "$existing_container"
fi

# Deploy the Docker container
docker run -d -p "$PORT":5000 --name  "$CONTAINER_NAME" --network demo-codex-network  "$IMAGE_ID"

if [ $? -eq 0 ]; then
    echo "Docker container '$CONTAINER_NAME' deployed successfully on port $PORT"
else
    echo "Failed to deploy Docker container '$CONTAINER_NAME'" >&2
    exit 1
fi
