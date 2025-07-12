#!/bin/bash

set -e

echo "Installing didc (Candid interface description language tool)..."
curl -fsSL -o /tmp/didc-linux64 https://github.com/dfinity/candid/releases/download/2024-07-29/didc-linux64 && \
    chmod +x /tmp/didc-linux64 && \
    mv /tmp/didc-linux64 /usr/bin/didc

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting dfx..."
dfx start --clean --background

echo "Running performance tests..."
python -u run_test_performance.py

echo "All done!"
