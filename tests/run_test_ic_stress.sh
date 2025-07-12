#!/bin/bash
set -e
set -x

IMAGE_ADDRESS="ghcr.io/smart-social-contracts/icp-dev-env:latest"

echo "Running IC stress tests..."
docker run --rm \
    -v "${PWD}/src:/app/src" \
    -v "${PWD}/../kybra_simple_db:/app/src/kybra_simple_db" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/../requirements.txt:/app/requirements.txt" \
    -v "${PWD}/entrypoint_stress.sh:/app/entrypoint.sh" \
    --entrypoint "/app/entrypoint.sh" \
    $IMAGE_ADDRESS stress || {
    echo "❌ IC stress tests failed"
    exit 1
}

echo "✅ IC stress tests completed successfully!"
