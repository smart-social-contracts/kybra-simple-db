#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

# Define a list of test identifiers
TEST_ID=('stress')

# Loop through each test identifier
echo "Testing test_${TEST_ID} module..."

echo "Starting dfx..."
dfx start --clean --background

echo "Deploying test canister..."
dfx deploy


for i in {1..10}
do
  echo "Running test_${TEST_ID}.run() function..."
  TEST_RESULT=$(dfx canister call test run_test ${TEST_ID})
  if [ "$TEST_RESULT" != '(0 : int)' ]; then
    echo "Error: test_${TEST_ID}.run() function returned unexpected result: $TEST_RESULT"
    dfx stop
    exit 1
  else
    echo "test_${TEST_ID}.run() function test passed!"
  fi
done


echo "Stopping dfx..."
dfx stop

echo "All done!"
