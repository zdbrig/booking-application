#!/bin/bash

# Define custom exit codes
EXIT_CODE_DOCKER_BUILD_FAILED=5
EXIT_CODE_JSON_VALIDATION_FAILED=6

# Check for docker-config.json and process it
if [ -f "docker-config.json" ]; then
    # Validate JSON file using jq
    if ! jq empty "docker-config.json"; then
        echo "Error: docker-config.json contains invalid JSON." >&2
        exit $EXIT_CODE_JSON_VALIDATION_FAILED
    fi

    # Extract image name from JSON
    image_name=$(jq -r '.image_name' "docker-config.json")
else
    image_name="ba157d16-cea0-4551-9eab-a58ba2421c9c"  # Default to jobId if no config file
fi

# Build the Docker image
echo "Building Docker image for $image_name..."
if docker build -t "$image_name" .; then
    echo "Docker image built successfully for $image_name."
else
    echo "Error: Failed to build Docker image for $image_name." >&2
    exit $EXIT_CODE_DOCKER_BUILD_FAILED
fi