#!/bin/bash
# Script to build multi-architecture Docker images for different transport mechanisms
set -e

# Parse command line arguments
PUSH=false
LOCAL_BUILD=true
REGISTRY="ghcr.io"
OWNER="zoharbabin"
REPO="kaltura-mcp"
PLATFORMS="linux/amd64,linux/arm64"
VERSION=$(grep -m 1 'version' pyproject.toml | cut -d'"' -f2)
COMMIT_SHA=$(git rev-parse --short HEAD)
TAG=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --push)
            PUSH=true
            LOCAL_BUILD=false
            shift
            ;;
        --registry)
            REGISTRY="$2"
            shift
            shift
            ;;
        --owner)
            OWNER="$2"
            shift
            shift
            ;;
        --repo)
            REPO="$2"
            shift
            shift
            ;;
        --platforms)
            PLATFORMS="$2"
            shift
            shift
            ;;
        --tag)
            TAG="$2"
            shift
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--push] [--registry REGISTRY] [--owner OWNER] [--repo REPO] [--platforms PLATFORMS] [--tag TAG]"
            exit 1
            ;;
    esac
done

# Check if Docker buildx is available
if ! docker buildx version > /dev/null 2>&1; then
  echo "Docker buildx is not available. Please install it first."
  exit 1
fi

# Create a new builder instance if it doesn't exist
if ! docker buildx inspect transport-builder > /dev/null 2>&1; then
  echo "Creating a new builder instance..."
  docker buildx create --name transport-builder --use
fi

# Check if we need to authenticate with the registry
if [ "$PUSH" = true ]; then
  echo "Checking authentication for ${REGISTRY}..."
  if [ "$REGISTRY" = "ghcr.io" ]; then
    echo "For GitHub Container Registry, make sure you're authenticated with:"
    echo "  export CR_PAT=YOUR_GITHUB_TOKEN"
    echo "  echo \$CR_PAT | docker login ghcr.io -u USERNAME --password-stdin"
    
    # Check if already logged in
    if ! docker buildx imagetools inspect ${REGISTRY}/${OWNER}/${REPO}:latest &>/dev/null; then
      if [ -z "$CR_PAT" ]; then
        echo "Error: GitHub token not found in CR_PAT environment variable."
        echo "Please set it and try again."
        exit 1
      fi
      
      echo "Logging in to GitHub Container Registry..."
      echo "$CR_PAT" | docker login ghcr.io -u "$OWNER" --password-stdin
    fi
  fi
fi

# Set build options based on push flag
if [ "$PUSH" = true ]; then
  BUILD_ARGS="--push"
elif [ "$LOCAL_BUILD" = true ]; then
  BUILD_ARGS="--load"
else
  BUILD_ARGS="--output type=image,push=false"
fi

# If a custom tag is provided, use it instead of the default tags
if [ -n "$TAG" ]; then
  echo "Building image with custom tag: ${TAG}..."
  docker buildx build \
    --platform ${PLATFORMS} \
    --tag ${TAG} \
    ${BUILD_ARGS} \
    .
else
  # Build the base image with default tags
  echo "Building the base image..."
  docker buildx build \
    --platform ${PLATFORMS} \
    --tag ${REGISTRY}/${OWNER}/${REPO}:latest \
    --tag ${REGISTRY}/${OWNER}/${REPO}:${VERSION} \
    --tag ${REGISTRY}/${OWNER}/${REPO}:${COMMIT_SHA} \
    ${BUILD_ARGS} \
    .

  # Build transport-specific images
  for TRANSPORT in stdio http sse; do
    echo "Building the ${TRANSPORT} transport image..."
    docker buildx build \
      --platform ${PLATFORMS} \
      --tag ${REGISTRY}/${OWNER}/${REPO}:${TRANSPORT} \
      --tag ${REGISTRY}/${OWNER}/${REPO}:${VERSION}-${TRANSPORT} \
      --tag ${REGISTRY}/${OWNER}/${REPO}:${COMMIT_SHA}-${TRANSPORT} \
      --build-arg KALTURA_MCP_TRANSPORT=${TRANSPORT} \
      ${BUILD_ARGS} \
      .
  done
fi

echo "All images built successfully!"
if [ "$PUSH" = true ]; then
  echo "Images pushed to registry."
fi

if [ -n "$TAG" ]; then
  echo "Built image with custom tag:"
  echo "- ${TAG}"
else
  echo "Available images:"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:latest (default)"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${VERSION}"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${COMMIT_SHA}"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:stdio (STDIO transport)"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${VERSION}-stdio"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${COMMIT_SHA}-stdio"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:http (HTTP transport)"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${VERSION}-http"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${COMMIT_SHA}-http"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:sse (SSE transport)"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${VERSION}-sse"
  echo "- ${REGISTRY}/${OWNER}/${REPO}:${COMMIT_SHA}-sse"
fi