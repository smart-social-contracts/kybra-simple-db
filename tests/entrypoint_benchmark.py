"""Benchmark orchestrator for measuring IC instruction costs.

Deploys the test canister once and runs benchmark operations at different
DB sizes, collecting instruction counts from ic.performance_counter(0).
Each benchmark method clears the DB internally, so no redeploy is needed.
"""

import re
import subprocess
import sys

TIMEOUT_MAX = 120
DB_SIZES = [0, 10, 50, 100, 200, 500]

OPERATIONS = [
    "create_entity",
    "load_level1",
    "load_level3",
    "serialize",
    "deserialize_new_level1",
    "deserialize_new_level3",
    "deserialize_existing_level1",
    "deserialize_existing_level3",
    "bulk_deserialize_level1",
    "bulk_deserialize_level3",
]

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def run_command(command, timeout=None):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        print(f"{RED}Command timed out after {timeout}s: {command}{RESET}", flush=True)
        return None, None
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed: {command}{RESET}", flush=True)
        print(f"stdout: {e.stdout}", flush=True)
        print(f"stderr: {e.stderr}", flush=True)
        return None, e.stderr


def run_benchmark(operation, db_size):
    """Run a single benchmark operation and extract instruction count."""
    cmd = (
        f'dfx canister call test run_test \'("benchmark", "{operation}", "{db_size}")\''
    )
    stdout, stderr = run_command(cmd, timeout=TIMEOUT_MAX)

    if stdout is None:
        return None

    # Extract BENCH_RESULT from stderr (ic.print goes to stderr via dfx)
    all_output = (stdout or "") + "\n" + (stderr or "")
    match = re.search(r"BENCH_RESULT:\w+:\d+:(\d+)", all_output)
    if match:
        return int(match.group(1))

    print(
        f"{YELLOW}  Could not parse result for {operation}@{db_size}{RESET}", flush=True
    )
    print(f"  stdout: {stdout[:200] if stdout else 'None'}", flush=True)
    print(f"  stderr: {stderr[:200] if stderr else 'None'}", flush=True)
    return None


def format_instructions(n):
    """Format instruction count with commas."""
    if n is None:
        return "        FAILED"
    return f"{n:>14,}"


def main():
    results = {}  # (operation, db_size) -> instruction_count

    print(f"\n{BOLD}{'='*70}")
    print(f"  kybra-simple-db Benchmark — IC Instruction Costs")
    print(f"{'='*70}{RESET}\n")

    total = len(DB_SIZES) * len(OPERATIONS)
    done = 0

    for db_size in DB_SIZES:
        print(f"\n{BOLD}--- DB Size: {db_size} entity pairs ---{RESET}")

        for op in OPERATIONS:
            done += 1
            print(
                f"  [{done}/{total}] {op} @ db_size={db_size}...", end=" ", flush=True
            )
            cost = run_benchmark(op, db_size)
            results[(op, db_size)] = cost
            if cost is not None:
                print(f"{GREEN}{cost:,} instructions{RESET}", flush=True)
            else:
                print(f"{RED}FAILED{RESET}", flush=True)

    # Print results table
    print(f"\n\n{BOLD}{'='*90}")
    print(f"  RESULTS TABLE")
    print(f"{'='*90}{RESET}\n")

    # Header
    header = f"{'Operation':<40}"
    for size in DB_SIZES:
        header += f"{'db=' + str(size):>14}"
    print(header)
    print("-" * (40 + 14 * len(DB_SIZES)))

    for op in OPERATIONS:
        row = f"{op:<40}"
        for size in DB_SIZES:
            row += format_instructions(results.get((op, size)))
        print(row)

    # Print level comparison summary
    print(f"\n\n{BOLD}--- Level Comparison (level=1 vs level=3) ---{RESET}\n")
    comparisons = [
        ("load_level1", "load_level3", "load"),
        ("deserialize_new_level1", "deserialize_new_level3", "deserialize (new)"),
        (
            "deserialize_existing_level1",
            "deserialize_existing_level3",
            "deserialize (existing)",
        ),
        (
            "bulk_deserialize_level1",
            "bulk_deserialize_level3",
            "bulk deserialize (10 records)",
        ),
    ]

    header = f"{'Operation':<35}{'DB Size':>8}  {'level=1':>14}  {'level=3':>14}  {'Savings':>10}"
    print(header)
    print("-" * 90)

    for l1_op, l3_op, label in comparisons:
        for size in DB_SIZES:
            l1 = results.get((l1_op, size))
            l3 = results.get((l3_op, size))
            if l1 is not None and l3 is not None and l3 > 0:
                savings = ((l3 - l1) / l3) * 100
                color = GREEN if savings > 0 else RED
                row = f"{label:<35}{size:>8}  {l1:>14,}  {l3:>14,}  {color}{savings:>9.1f}%{RESET}"
            else:
                row = f"{label:<35}{size:>8}  {'N/A':>14}  {'N/A':>14}  {'N/A':>10}"
            print(row)

    print(f"\n{BOLD}Benchmark complete.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
