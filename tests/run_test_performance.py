#!/usr/bin/env python3

import ast
import traceback

from get_canister_status import get_canister_status_json
from utils import check_value, run_command

CANISTER_NAME = "test_performance"  # Name of the Internet Computer canister to deploy
NUM_RECORDS = 1000  # Number of records to insert per batch during performance testing
NUM_BATCHES = 10  # Total number of batches to process during the test
MAP_MAX_VALUE_SIZE = 1000  # Maximum size for map values in the database schema

STABLEBTREEMAP_STABLE_SIZE_BASE = 64 * 1024
STABLEBTREEMAP_STABLE_SIZE_CHUNK = 8 * 1024 * 1024


# Performance validation threshold - the maximum allowed ratio between actual and expected stable memory size of a record
EXPECTED_MAX_EFFICIENCY_RATIO = 3

# Running counters for performance metrics
total_count_inserts = 0  # Tracks the total number of successful insert operations
code_memory = None  # The memory size used for the canister code


def print_analysis_explanation():
    print("=" * 50)
    print("\nAnalysis explanation:")
    print(
        "- stable_memory_size: The amount of memory used by the canister for storing data that persists across upgrades but is lost after a canister re-installation."
    )
    print(
        "- global_memory_size: (this value is given by the management canister and seems to be wrong for some unknown reasons)."
    )
    print(
        "- wasm_memory_size: The amount of memory used by the canister for storing the canister code, volatile memory and stable memory."
    )
    print(
        "- Volatile memory: The amount of memory used by the canister for executing code. It is lost after a canister upgrade or re-installation."
    )
    print(
        "- Stable memory per record: The average amount of stable memory used per record in the database."
    )
    print(
        "- Stable memory efficiency ratio:: The ratio of actual stable memory per record to the minimum theorical value size. The lower the better (more efficient)."
    )
    print("=" * 50)


def get_db_canister_status(canister_principal_id):
    """Get canister status using dfx command line."""
    # Run dfx command to get canister status
    dfx_command = f"""dfx canister call "{canister_principal_id}" status"""
    status_response = run_command(dfx_command)

    try:
        # Remove outer quotes and parentheses
        status_str = status_response.strip().strip("()\"'")
        # Replace escaped single quotes
        status_str = status_str.replace("\\'", "'")
        # Use ast.literal_eval to safely convert to dict
        status_dict = ast.literal_eval(status_str)
        return status_dict["count_inserts"], status_dict["count_updates"]
    except Exception as e:
        print(f"Error parsing status: {e}\n{traceback.format_exc()}")
        return 0, 0


def analyze_performance(canister_id):

    # Get memory metrics from management canister
    metrics_with_data = get_canister_status_json(canister_id)
    for tag in ["stable_memory_size", "global_memory_size", "wasm_memory_size"]:
        print(f"{tag}: {metrics_with_data['memory_metrics'][tag]} bytes")

    global code_memory
    if not code_memory:
        code_memory = metrics_with_data["memory_metrics"]["wasm_memory_size"]

    volatile_memory = (
        metrics_with_data["memory_metrics"]["wasm_memory_size"] - code_memory
    )
    print(f"Volatile memory: {volatile_memory} bytes")

    # Calculate memory per record and efficiency ratio
    if total_count_inserts > 0:
        stable_memory_per_record = (
            metrics_with_data["memory_metrics"]["stable_memory_size"]
            / total_count_inserts
        )
        print(f"Stable memory per record: {stable_memory_per_record:.2f} bytes")
        efficiency_ratio = stable_memory_per_record / MAP_MAX_VALUE_SIZE
        print(f"Stable memory efficiency ratio: {efficiency_ratio:.2f}")
    else:
        print("No records inserted yet")
        stable_memory_per_record = 0
        efficiency_ratio = 0

    return (
        metrics_with_data["memory_metrics"]["stable_memory_size"],
        stable_memory_per_record,
        efficiency_ratio,
    )


def main():

    global total_count_inserts
    total_count_inserts = 0

    print("=" * 50)
    print("Starting performance test")
    print("=" * 50)

    print_analysis_explanation()

    print("[Step 1] Deploying canister...")
    run_command(f"dfx deploy {CANISTER_NAME}")
    canister_id = run_command(f"dfx canister id {CANISTER_NAME}").strip()
    print(f"Canister ID: {canister_id}")

    analyze_performance(canister_id)

    print("\n[Step 2] Inserting test records")
    run_command(f"dfx canister call {CANISTER_NAME} insert_records '({NUM_RECORDS})'")
    # result = int(result.strip())
    # assert result == NUM_RECORDS
    count_inserts, _ = get_db_canister_status(canister_id)
    print(f"Total inserted records: {count_inserts}")
    check_value(count_inserts, NUM_RECORDS)
    total_count_inserts += NUM_RECORDS
    check_value(total_count_inserts, count_inserts)

    stable_memory_size, _, _ = analyze_performance(canister_id)

    check_value(
        stable_memory_size,
        STABLEBTREEMAP_STABLE_SIZE_BASE + STABLEBTREEMAP_STABLE_SIZE_CHUNK,
    )

    for i in range(NUM_BATCHES):
        print(f"\n[Step 3] Inserting {NUM_RECORDS} records (batch {i+1}/{NUM_BATCHES})")
        run_command(
            f"dfx canister call {CANISTER_NAME} insert_records '({NUM_RECORDS})'"
        )
        # result = int(result.strip())
        # assert result == NUM_RECORDS
        count_inserts, _ = get_db_canister_status(canister_id)
        print(f"Total inserted records: {count_inserts}")
        total_count_inserts += NUM_RECORDS
        check_value(total_count_inserts, count_inserts)

        analyze_performance(canister_id)

    stable_memory_size, stable_memory_per_record, efficiency_ratio = (
        analyze_performance(canister_id)
    )

    check_value(
        stable_memory_size,
        STABLEBTREEMAP_STABLE_SIZE_BASE + STABLEBTREEMAP_STABLE_SIZE_CHUNK * 3,
    )

    print("\n[Step 4] Checking stable_memory_size is below the expected limit")
    check_value(
        stable_memory_size,
        EXPECTED_MAX_EFFICIENCY_RATIO
        * MAP_MAX_VALUE_SIZE
        * NUM_RECORDS
        * (NUM_BATCHES + 1),
        "<",
    )
    print("\n[Step 5] Checking stable_memory_per_record is below the expected limit")
    check_value(
        stable_memory_per_record,
        EXPECTED_MAX_EFFICIENCY_RATIO * MAP_MAX_VALUE_SIZE,
        "<",
    )
    print("\n[Step 6] Checking efficiency_ratio is below the expected limit")
    check_value(efficiency_ratio, EXPECTED_MAX_EFFICIENCY_RATIO, "<")

    print("\n[Step 7] Upgrading canister (persistent memory should be preserved)")
    run_command(f"dfx deploy {CANISTER_NAME} --mode=upgrade")

    print("\n[Step 8] Measuring memory usage after upgrade")
    analyze_performance(canister_id)

    print("\n[Step 9] Reinstalling canister (persistent memory should be deleted)")
    run_command(f"dfx deploy {CANISTER_NAME} --mode=reinstall --yes")
    total_count_inserts = 0
    stable_memory_size, _, _ = analyze_performance(canister_id)

    print("\n[Step 10] Checking stable memory has been cleaned")
    check_value(stable_memory_size, 0)

    print("\n" + "=" * 50)
    print("SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()
