#!/bin/bash

# Constants
CONTAINER_NAME="random-room-generator-service-sqoin-sqoin"
PORT="5005"
IMAGE_ID="ba157d16-cea0-4551-9eab-a58ba2421c9c"

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