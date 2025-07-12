#!/bin/bash

set -e

echo "Installing dependencies..."
pip install -r requirements.txt

# Define a list of test identifiers
TEST_IDS=('example_1' 'example_2' 'entity' 'mixins' 'properties' 'relationships' 'database' 'audit' 'stress' 'benchmarks')

# Loop through each test identifier
for TEST_ID in "${TEST_IDS[@]}"; do
  echo "Testing test_${TEST_ID} module..."

  echo "Starting dfx..."
  dfx start --clean --background

  echo "Deploying test canister..."
  dfx deploy

  TEST_RESULT=$(dfx canister call test run_test ${TEST_ID})
  if [ "$TEST_RESULT" != '(0 : int)' ]; then
    echo "Error: test_${TEST_ID}.run() function returned unexpected result: $TEST_RESULT"
    dfx stop
    exit 1
  else
    echo "test_${TEST_ID}.run() function test passed!"

    echo "Testing upgrade persistence check..."

    echo "Getting database dump before upgrade..."
    BEFORE_UPGRADE=$(dfx canister call test dump_json)

    echo "Upgrading canister..."
    dfx deploy --mode=upgrade

    echo "Getting database dump after upgrade..."
    AFTER_UPGRADE=$(dfx canister call test dump_json)

    if [ "$BEFORE_UPGRADE" != "$AFTER_UPGRADE" ]; then
      echo "ERROR: Database content changed after upgrade!"
      echo "Before: $BEFORE_UPGRADE"
      echo "After: $AFTER_UPGRADE"
      exit 1
    else
      echo "Upgrade persistence test passed! Database content maintained across upgrade."
    fi

  fi

  echo "Stopping dfx..."
  dfx stop
done

echo "Testing specific upgrade persistence check..."
echo "Starting dfx..."
dfx start --clean --background

echo "Deploying test canister..."
dfx deploy

TEST_ID="upgrade_before"
TEST_RESULT=$(dfx canister call test run_test ${TEST_ID})
if [ "$TEST_RESULT" != '(0 : int)' ]; then
  echo "Error: test_${TEST_ID}.run() function returned unexpected result: $TEST_RESULT"
  dfx stop
  exit 1
fi

echo "Getting database dump before upgrade..."
BEFORE_UPGRADE=$(dfx canister call test dump_json)

echo "Testing upgrade persistence check..."
echo "Upgrading canister..."
dfx deploy --mode=upgrade

echo "Getting database dump after upgrade..."
AFTER_UPGRADE=$(dfx canister call test dump_json)

echo "Before: $BEFORE_UPGRADE"
echo "After: $AFTER_UPGRADE"

if [ "$BEFORE_UPGRADE" != "$AFTER_UPGRADE" ]; then
  echo "ERROR: Database content changed after upgrade!"
  exit 1
fi

TEST_ID="upgrade_after"
TEST_RESULT=$(dfx canister call test run_test ${TEST_ID})
if [ "$TEST_RESULT" != '(0 : int)' ]; then
  echo "Error: test_${TEST_ID}.run() function returned unexpected result: $TEST_RESULT"
  exit 1
fi

echo "Upgrade persistence test passed! Database logic consistent across upgrade."

echo "Stopping dfx..."
dfx stop

echo "All done!"
