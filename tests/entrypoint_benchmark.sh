#!/bin/bash
set -e
set -x

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting dfx..."
dfx start --clean --background

echo "Deploying test canister..."
dfx deploy

echo "Running benchmarks..."
python -u entrypoint_benchmark.py

echo "Stopping dfx..."
dfx stop
