#!/bin/bash
# Simple script to run all linters from CI workflow locally
# Usage: ./run_linters.sh [--fix]
#   --fix    Apply fixes automatically when possible (black, isort)

# Exit on first error
set -e

# Check if required linting tools are installed
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo "Error: $1 is not installed or not in PATH"
        echo "Install it with: pip install $1"
        exit 1
    fi
}

check_command black
check_command isort
check_command flake8
check_command mypy

# Check if we should fix issues or just check
FIX_MODE=false
if [ "$1" == "--fix" ]; then
    FIX_MODE=true
    echo "Running linters in FIX mode..."
else
    echo "Running linters in CHECK mode (use --fix to auto-format)..."
fi

# Check/fix formatting with black
echo "Running black..."
if [ "$FIX_MODE" = true ]; then
    black kybra_simple_db tests
else
    black kybra_simple_db tests --check
fi

# Check/fix imports with isort
echo "Running isort..."
if [ "$FIX_MODE" = true ]; then
    isort kybra_simple_db tests
else
    isort kybra_simple_db tests --check-only
fi

# Lint with flake8 (no auto-fix available)
echo "Running flake8..."
# Using configuration from setup.cfg
flake8 kybra_simple_db tests --exclude=tests/venv,tests/.kybra,*/.kybra/*,*/__pycache__/*

# Type check with mypy (no auto-fix available)
echo "Running mypy..."
# Using configuration from setup.cfg
mypy kybra_simple_db tests

echo "All linters completed successfully!"
