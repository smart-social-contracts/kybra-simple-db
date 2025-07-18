import subprocess
import sys
import time

TIMEOUT_MAX = 30
BULK_INSERT_COUNT = 100
MAX_ITERATIONS = 5
MIN_ITERATIONS = 2

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


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
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Error executing command: {command}", flush=True)
        print(f"Error occurred after {elapsed_time:.2f} seconds", flush=True)
        print(f"Error: {e}", flush=True)
        print(f"Output: {e.stdout}", flush=True)
        print(f"Error output: {e.stderr}", flush=True)
        sys.exit(2)


def main():
    try:
        print(
            "Starting stress test with %d iterations and %d entities per iteration"
            % (MAX_ITERATIONS, BULK_INSERT_COUNT)
        )
        count = 0
        for i in range(1, MAX_ITERATIONS + 1):
            print(f"Running iteration {i}/{MAX_ITERATIONS}")
            run_command(
                'dfx canister call test run_test \'("stress", "bulk_insert", "%d")\''
                % BULK_INSERT_COUNT,
                timeout=TIMEOUT_MAX,
            )
            count += BULK_INSERT_COUNT
            name = "Entity_%s" % (count - 1)
            run_command(
                'dfx canister call test run_test \'("stress", "query", "%s")\'' % name,
                timeout=TIMEOUT_MAX,
            )
    except Exception as e:
        print("Error running test after %d iterations" % i)
        print("Exception: %s" % e)
    finally:
        if i >= MIN_ITERATIONS:
            print(f"{GREEN}Test SUCCESS after {i} iterations{RESET}")
            return 0
        else:
            print(f"{RED}Test FAILED after {i} iterations{RESET}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
