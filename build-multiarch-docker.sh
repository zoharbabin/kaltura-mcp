#!/bin/bash
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Parse command line arguments
PUSH=false
TAG="kaltura-mcp:local"
REGISTRY=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --push)
            PUSH=true
            shift
            ;;
        --tag)
            TAG="$2"
            shift
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--push] [--tag TAG] [--registry REGISTRY]"
            exit 1
            ;;
    esac
done

# Detect architecture
ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    PLATFORM="linux/arm64"
    echo "Detected ARM64 architecture"
else
    PLATFORM="linux/amd64"
    echo "Detected AMD64 architecture"
fi

# Build Docker image for the current architecture
echo "Building Docker image for $PLATFORM..."
docker build \
    --platform $PLATFORM \
    --tag $TAG \
    .

echo "Docker image built successfully for $PLATFORM!"

# Push to registry if requested
if [ "$PUSH" = true ] && [ ! -z "$REGISTRY" ]; then
    echo "Pushing image to $REGISTRY..."
    REMOTE_TAG="$REGISTRY/$TAG"
    docker tag $TAG $REMOTE_TAG
    docker push $REMOTE_TAG
    echo "Image pushed successfully to $REMOTE_TAG"
fi

echo "You can now run the container with:"
echo "docker run -p 8000:8000 -v \$(pwd)/config.yaml:/app/config.yaml $TAG"

echo ""
echo "Note: This image is built only for your current architecture ($PLATFORM)."
echo "For multi-architecture builds, use the GitHub Actions workflow."