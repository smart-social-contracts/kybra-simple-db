#!/bin/bash
set -e
set -x

echo "Running stress tests and benchmarks..."

cd src

exit_code=0

python -c "import psutil" 2>/dev/null || pip install psutil

echo "Running stress tests..."
PYTHONPATH="../..:." python tests/test_stress.py || exit_code=1

echo "Running benchmarks..."
PYTHONPATH="../..:." python tests/test_benchmarks.py || exit_code=1

if [ $exit_code -eq 0 ]; then
  echo -e "\033[0;32mAll stress tests and benchmarks completed successfully!\033[0m"
else
  echo -e "\033[0;31mSome stress tests or benchmarks failed. Please check the logs.\033[0m"
fi

exit $exit_code
