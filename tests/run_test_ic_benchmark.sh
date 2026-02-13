#!/bin/bash
set -e
set -x

IMAGE_ADDRESS="ghcr.io/smart-social-contracts/icp-dev-env:latest"

echo "Running benchmarks..."
docker run --rm \
    -v "${PWD}/src:/app/src" \
    -v "${PWD}/../kybra_simple_db:/app/src/kybra_simple_db" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/../requirements.txt:/app/requirements.txt" \
    -v "${PWD}/entrypoint_benchmark.sh:/app/entrypoint_benchmark.sh" \
    -v "${PWD}/entrypoint_benchmark.py:/app/entrypoint_benchmark.py" \
    --entrypoint "/app/entrypoint_benchmark.sh" \
    $IMAGE_ADDRESS || {
    echo "❌ Benchmarks failed"
    exit 1
}

echo "✅ Benchmarks completed successfully!"
