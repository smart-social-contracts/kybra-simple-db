import subprocess
import sys
import time

TIMEOUT_MAX = 10


def run_command(command, check=True, timeout=None):
    """Run a shell command and return its output"""
    print(f"Running command: {command}", flush=True)
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(
            f"Command output: {result.stdout[:100]}{'...' if len(result.stdout) > 100 else ''}",
            flush=True,
        )
        print(f"Command executed in {elapsed_time:.2f} seconds", flush=True)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Command timed out after {timeout} seconds: {command}", flush=True)
        print(f"Elapsed time before timeout: {elapsed_time:.2f} seconds", flush=True)
        return None
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Error executing command: {command}", flush=True)
        print(f"Error occurred after {elapsed_time:.2f} seconds", flush=True)
        print(f"Error: {e}", flush=True)
        print(f"Output: {e.stdout}", flush=True)
        print(f"Error output: {e.stderr}", flush=True)
        if check:
            sys.exit(1)
        return None


def main():

    num_iterations = 100
    for i in range(1, num_iterations + 1):
        run_command(
            'dfx canister call test run_test \'("stress", "test_bulk_insertion_and_load_small", "")\'',
            timeout=TIMEOUT_MAX,
        )
        run_command(
            'dfx canister call test run_test \'("stress", "test_query_performance_after_bulk_insert", "")\'',
            timeout=TIMEOUT_MAX,
        )


if __name__ == "__main__":
    main()
