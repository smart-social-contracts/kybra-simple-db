#!/bin/bash
set -e
set -x

echo "Running tests..."

exit_code=0

TEST_IDS=("1" "2" "entity" "mixins" "properties" "relationships" "database" "storage")

for TEST_ID in "${TEST_IDS[@]}"; do
  PYTHONPATH=.. python tests/test_${TEST_ID}.py || exit_code=1
done

if [ $exit_code -eq 0 ]; then
  echo -e "\033[0;32mAll tests passed successfully!\033[0m"
else
  echo -e "\033[0;31mSome tests failed. Please check the logs.\033[0m"
fi

exit $exit_code
