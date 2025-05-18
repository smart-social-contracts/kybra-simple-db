#!/usr/bin/env python3

import json
import re
import sys

from utils import run_command


def get_canister_status(canister_principal_id):
    """Get canister status using dfx command line."""
    # Run dfx command to get canister status
    dfx_command = f"""dfx canister call aaaaa-aa canister_status '(record {{ canister_id = principal "{canister_principal_id}" }})' --output raw > response.did"""
    run_command(dfx_command)

    # Use didc to decode the response
    didc_command = "cat response.did | didc decode -d management.did -m canister_status"
    decoded_output = run_command(didc_command)

    return decoded_output


def parse_nat_value(pattern, output):
    """Extract a NAT value from the output using regex."""
    match = re.search(pattern, output)
    if match:
        return int(match.group(1).replace("_", ""))
    return None


def parse_vec_principals(pattern, output):
    """Extract a vector of principals from the output."""
    # Find the section that contains the vector of principals
    match = re.search(pattern, output, re.DOTALL)
    if not match:
        return []

    # Extract all principals from the matched section
    principals = re.findall(r'principal "([^"]+)"', match.group(1))
    return principals


def parse_variant(pattern, output):
    """Extract a variant value from the output."""
    match = re.search(pattern, output)
    if match:
        return match.group(1)
    return None


def extract_canister_status(output):
    """Extract all canister status from the decoded output."""
    # Memory metrics
    memory_metrics = {
        "wasm_binary_size": parse_nat_value(
            r"wasm_binary_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "wasm_chunk_store_size": parse_nat_value(
            r"wasm_chunk_store_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "canister_history_size": parse_nat_value(
            r"canister_history_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "stable_memory_size": parse_nat_value(
            r"stable_memory_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "snapshots_size": parse_nat_value(
            r"snapshots_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "wasm_memory_size": parse_nat_value(
            r"wasm_memory_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "global_memory_size": parse_nat_value(
            r"global_memory_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "custom_sections_size": parse_nat_value(
            r"custom_sections_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
    }

    # Total memory size
    memory_size = parse_nat_value(r"memory_size\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output)

    # Status
    status = parse_variant(r"status\s*=\s*variant\s*{\s*([^}]+)\s*}", output)

    # Cycles
    cycles = parse_nat_value(r"cycles\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output)

    # Settings
    settings = {
        "freezing_threshold": parse_nat_value(
            r"freezing_threshold\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "wasm_memory_threshold": parse_nat_value(
            r"wasm_memory_threshold\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "controllers": parse_vec_principals(
            r"controllers\s*=\s*vec\s*{([^}]+)}", output
        ),
        "reserved_cycles_limit": parse_nat_value(
            r"reserved_cycles_limit\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "log_visibility": parse_variant(
            r"log_visibility\s*=\s*variant\s*{\s*([^}]+)\s*}", output
        ),
        "wasm_memory_limit": parse_nat_value(
            r"wasm_memory_limit\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "memory_allocation": parse_nat_value(
            r"memory_allocation\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "compute_allocation": parse_nat_value(
            r"compute_allocation\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
    }

    # Query stats
    query_stats = {
        "response_payload_bytes_total": parse_nat_value(
            r"response_payload_bytes_total\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "num_instructions_total": parse_nat_value(
            r"num_instructions_total\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "num_calls_total": parse_nat_value(
            r"num_calls_total\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
        "request_payload_bytes_total": parse_nat_value(
            r"request_payload_bytes_total\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
        ),
    }

    # Other metrics
    idle_cycles_burned_per_day = parse_nat_value(
        r"idle_cycles_burned_per_day\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
    )

    # Module hash (optional)
    module_hash_match = re.search(r'module_hash\s*=\s*opt\s*blob\s*"([^"]*)"', output)
    module_hash = module_hash_match.group(1) if module_hash_match else None

    # Reserved cycles
    reserved_cycles = parse_nat_value(
        r"reserved_cycles\s*=\s*(\d+(?:_\d+)*)\s*:\s*nat", output
    )

    # Combine all results
    result = {
        "memory_metrics": memory_metrics,
        "status": status,
        "memory_size": memory_size,
        "cycles": cycles,
        "settings": settings,
        "query_stats": query_stats,
        "idle_cycles_burned_per_day": idle_cycles_burned_per_day,
        "module_hash": module_hash,
        "reserved_cycles": reserved_cycles,
    }

    return result


def get_canister_status_json(canister_principal_id):
    return extract_canister_status(get_canister_status(canister_principal_id))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(get_canister_status_json(sys.argv[1]), indent=2))
    else:
        raise Exception("Please provide a canister principal ID as an argument")
