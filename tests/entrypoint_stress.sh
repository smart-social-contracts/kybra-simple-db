#!/bin/bash

set -e
set -x

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting dfx..."
dfx start --clean --background

echo "Deploying test canister..."
dfx deploy

if python -u entrypoint_stress.py; then
    echo "✅ IC stress tests completed successfully!"
else
    echo "❌ IC stress tests failed"
    exit 1
fi
