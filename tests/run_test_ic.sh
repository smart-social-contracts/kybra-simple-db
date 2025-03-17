#!/bin/bash
set -e
set -x

echo "Running tests..."
docker run --rm \
    -v "${PWD}/src:/app/src" \
    -v "${PWD}/../kybra_simple_db:/app/src/kybra_simple_db" \
    -v "${PWD}/tests:/app/tests" \
    -v "${PWD}/dfx.json:/app/dfx.json" \
    -v "${PWD}/entrypoint.sh:/app/entrypoint.sh" \
    --entrypoint "/app/entrypoint.sh" \
    ghcr.io/smart-social-contracts/icp-dev-env:latest || {
    echo "❌ Tests failed"
    exit 1
}

echo "✅ All tests passed successfully!"