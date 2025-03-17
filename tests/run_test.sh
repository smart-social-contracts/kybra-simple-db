#!/bin/bash
set -e
set -x

echo "Running tests..."

PYTHONPATH=.. pytest tests --cov=kybra_simple_db --cov-report=xml