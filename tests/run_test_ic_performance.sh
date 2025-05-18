#!/bin/bash
set -e
set -x

IMAGE_ADDRESS="ghcr.io/smart-social-contracts/icp-dev-env:latest"

echo "Running tests..."
docker run --rm \
    -v "${PWD}/src:/app/src" \
    -v "${PWD}/../kybra_simple_db:/app/src/kybra_simple_db" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/../requirements.txt:/app/requirements.txt" \
    -v "${PWD}/entrypoint_performance.sh:/app/entrypoint.sh" \
    -v "${PWD}/run_test_performance.py:/app/run_test_performance.py" \
    -v "${PWD}/get_canister_status.py:/app/get_canister_status.py" \
    -v "${PWD}/utils.py:/app/utils.py" \
    --entrypoint "/app/entrypoint.sh" \
    $IMAGE_ADDRESS || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"