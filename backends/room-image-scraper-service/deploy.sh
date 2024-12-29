#!/bin/bash

# Constants
CONTAINER_NAME="room-image-scraper-service-sqoin-sqoin"
PORT="5022"
IMAGE_ID="80fd10ae-7e8c-4b55-b085-b6b5401cafbb"

# Check if a container with the same name already exists
existing_container=$(docker ps -aq -f name=^$CONTAINER_NAME$)
if [ ! -z "$existing_container" ]; then
    echo "Container with name $CONTAINER_NAME already exists, removing..."
    docker rm -f "$existing_container"
fi

# Deploy the Docker container
docker run -d -p "$PORT":5000 --name  "$CONTAINER_NAME" --hostname "$IMAGE_ID" --network demo-codex-network  "$IMAGE_ID"

if [ $? -eq 0 ]; then
    echo "Docker container '$CONTAINER_NAME' deployed successfully on port $PORT"
else
    echo "Failed to deploy Docker container '$CONTAINER_NAME'" >&2
    exit 1
fi
