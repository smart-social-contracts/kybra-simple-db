#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt


dfx start --clean --background

echo "Running performance tests..."
python run_test_performance.py

echo "All done!"
