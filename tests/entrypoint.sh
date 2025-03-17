#!/bin/bash
set -e
set -x

# Start dfx in the background
echo "Starting dfx..."
dfx start --background --clean

# Wait for dfx to be ready
echo "Waiting for dfx to start..."
sleep 10

# Deploy the hello canister
echo "Deploying hello canister..."
dfx deploy

# Call greet and check output
echo "Testing greet function..."
GREET_RESULT=$(dfx canister call test greet)
if [ "$GREET_RESULT" != '("Hello!")' ]; then
  echo "Error: greet function returned unexpected result: $GREET_RESULT"
  dfx stop
  exit 1
else
  echo "greet function test passed!"
fi

# Call test1 and check output
echo "Testing test1 function..."
TEST1_RESULT=$(dfx canister call test test1)
if [ "$TEST1_RESULT" != '("Test 1")' ]; then
  echo "Error: test1 function returned unexpected result: $TEST1_RESULT"
  dfx stop
  exit 1
else
  echo "test1 function test passed!"
fi

echo "Stopping dfx..."
dfx stop

echo "All done!"