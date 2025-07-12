#!/bin/bash
set -e
set -x

echo "Running IC stress tests and benchmarks..."

echo "Starting dfx..."
dfx start --clean --background

echo "Deploying test canister..."
dfx deploy

echo "Running stress tests in IC replica..."
STRESS_RESULT=$(dfx canister call test run_test stress)
if [ "$STRESS_RESULT" != '(0 : int)' ]; then
  echo "Error: stress tests returned unexpected result: $STRESS_RESULT"
  dfx stop
  exit 1
else
  echo "Stress tests passed!"
fi

echo "Running benchmarks in IC replica..."
BENCHMARK_RESULT=$(dfx canister call test run_test benchmarks)
if [ "$BENCHMARK_RESULT" != '(0 : int)' ]; then
  echo "Error: benchmarks returned unexpected result: $BENCHMARK_RESULT"
  dfx stop
  exit 1
else
  echo "Benchmarks passed!"
fi

echo "Stopping dfx..."
dfx stop

echo -e "\033[0;32mAll IC stress tests and benchmarks completed successfully!\033[0m"
