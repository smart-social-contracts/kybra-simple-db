#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running performance tests..."
python run_test_performance.py

echo "All done!"
