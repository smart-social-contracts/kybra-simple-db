#!/bin/bash
set -e
set -x

IMAGE_ADDRESS="ghcr.io/smart-social-contracts/icp-dev-env:latest"

echo "Pulling image..."
docker pull $IMAGE_ADDRESS

echo "Running tests..."
docker run --rm \
    -v "${PWD}/src:/app/src" \
    -v "${PWD}/../kybra_simple_db:/app/src/kybra_simple_db" \
    -v "${PWD}/tests:/app/tests" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/entrypoint.sh:/app/entrypoint.sh" \
    --entrypoint "/app/entrypoint.sh" \
    $IMAGE_ADDRESS || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"