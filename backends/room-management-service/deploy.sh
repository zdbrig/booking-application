#!/bin/bash

# Constants
CONTAINER_NAME="room-management-service-sqoin-sqoin"
PORT="5006"
IMAGE_ID="d6d87720-fa3d-4e2b-a4d5-745f94157ebf"

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
