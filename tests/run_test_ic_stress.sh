#!/bin/bash
set -e
set -x

IMAGE_ADDRESS="ghcr.io/smart-social-contracts/icp-dev-env:latest"

echo "Running IC stress tests and benchmarks..."
docker run --rm \
    -v "${PWD}/src:/app/src" \
    -v "${PWD}/../kybra_simple_db:/app/src/kybra_simple_db" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/../requirements.txt:/app/requirements.txt" \
    -v "${PWD}/entrypoint.sh:/app/entrypoint.sh" \
    --entrypoint "/app/entrypoint.sh" \
    $IMAGE_ADDRESS stress benchmarks || {
    echo "❌ IC stress tests failed"
    exit 1
}

echo "✅ IC stress tests and benchmarks completed successfully!"
