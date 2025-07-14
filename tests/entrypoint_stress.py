#!/usr/bin/env python3

import subprocess
import sys
import time
import os
import threading

# Define log file path - use absolute path that works in Docker
DFX_LOG_FILE = os.path.join(os.getcwd(), "dfx_output.log")
print(f"Log file will be at: {DFX_LOG_FILE}", flush=True)

def run_command(command, check=True, timeout=None):
    """Run a shell command and return its output"""
    print(f"Running command: {command}", flush=True)
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            text=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            timeout=timeout
        )
        print(f"Command output: {result.stdout[:100]}{'...' if len(result.stdout) > 100 else ''}", flush=True)
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"Command timed out after {timeout} seconds: {command}", flush=True)
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}", flush=True)
        print(f"Error: {e}", flush=True)
        print(f"Output: {e.stdout}", flush=True)
        print(f"Error output: {e.stderr}", flush=True)
        if check:
            sys.exit(1)
        return None

def dfx_is_running():
    """Check if dfx is running"""
    try:
        result = subprocess.run(
            "dfx ping", 
            shell=True, 
            check=False,
            text=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except Exception:
        return False

def tail_log_file(log_file):
    """Tail the log file in a separate thread and print new lines"""
    def tail_file():
        while True:
            try:
                with open(log_file, "r") as f:
                    # Move to the end of the file
                    f.seek(0, 2)
                    while True:
                        line = f.readline()
                        if not line:
                            time.sleep(0.1)
                            continue
                        if "error" in line.lower() or "exception" in line.lower():
                            print(f"\033[91m{line.strip()}\033[0m", flush=True)  # Red for errors
                        elif "warn" in line.lower():
                            print(f"\033[93m{line.strip()}\033[0m", flush=True)  # Yellow for warnings
                        else:
                            print(f"LOG: {line.strip()}", flush=True)
            except Exception as e:
                print(f"Error in log tailing thread: {e}", flush=True)
            time.sleep(10)
    
    # Start tailing in a separate thread
    thread = threading.Thread(target=tail_file, daemon=True)
    thread.start()
    return thread

def main():
    # Clean up any existing log file
    if os.path.exists(DFX_LOG_FILE):
        os.remove(DFX_LOG_FILE)
    
    # Install dependencies
    print("Installing dependencies...", flush=True)
    run_command("pip install -r requirements.txt")
    
    # Define a list of test identifiers
    test_ids = ["stress_bulk_insert", "stress_bulk_load"]
    
    # Loop through each test identifier
    for test_id in test_ids:
        print(f"Testing test_{test_id} module...", flush=True)
    
    # Start dfx with better handling for containerized environments
    print("Starting dfx...", flush=True)
    
    # Start log monitoring
    log_thread = None
    
    # Check if dfx is already running
    if dfx_is_running():
        print("dfx is already running, using existing instance", flush=True)
    else:
        print("Starting new dfx instance with log file", flush=True)
        # Start dfx in a way that works better in containers, with log output to file
        dfx_start_cmd = f"dfx start --clean --log tee --logfile {DFX_LOG_FILE}"
        dfx_process = subprocess.Popen(dfx_start_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Start tailing the log file
        log_thread = tail_log_file(DFX_LOG_FILE)
        
        # Give dfx time to start
        print("Waiting for dfx to start...", flush=True)
        max_wait = 60  # seconds - increased timeout for container environment
        start_time = time.time()
        
        while not dfx_is_running() and (time.time() - start_time) < max_wait:
            print(".", end="", flush=True)
            time.sleep(1)
        
        print("", flush=True)  # New line after progress dots
        
        if not dfx_is_running():
            print("Failed to start dfx after waiting. Exiting.", flush=True)
            # Print recent log entries to help with debugging
            if os.path.exists(DFX_LOG_FILE):
                print("\nLast 20 lines of dfx log:", flush=True)
                run_command(f"tail -n 20 {DFX_LOG_FILE}")
            
            run_command("pkill -f dfx", check=False)
            sys.exit(1)
    
    # Deploy test canister
    print("Deploying test canister...", flush=True)
    deploy_result = run_command("dfx deploy", timeout=120)
    
    if not deploy_result:
        print("Failed to deploy canister. Exiting.", flush=True)
        # Print recent log entries to help with debugging
        if os.path.exists(DFX_LOG_FILE):
            print("\nLast 20 lines of dfx log:", flush=True)
            run_command(f"tail -n 20 {DFX_LOG_FILE}")
        
        run_command("dfx stop", check=False)
        sys.exit(1)
    
    num_iterations = 100
    
    try:
        # Loop through iterations
        for i in range(1, num_iterations + 1):
            # Loop through test IDs
            for test_id in test_ids:
                print(f"Running test_{test_id}.run() function (iteration {i}/{num_iterations})...", flush=True)
                test_result = run_command(f"dfx canister call test run_test {test_id}", timeout=180)
                
                if not test_result:
                    print(f"Error: test_{test_id}.run() function timed out or failed", flush=True)
                    # Print recent log entries to help with debugging
                    if os.path.exists(DFX_LOG_FILE):
                        print("\nLast 50 lines of dfx log:", flush=True)
                        run_command(f"tail -n 50 {DFX_LOG_FILE} | grep -i -E 'error|exception|fail'")
                    
                    run_command("dfx stop", check=False)
                    sys.exit(1)
                elif test_result != "(0 : int)":
                    print(f"Error: test_{test_id}.run() function returned unexpected result: {test_result}", flush=True)
                    # Print recent log entries to help with debugging
                    if os.path.exists(DFX_LOG_FILE):
                        print("\nLast 50 lines of dfx log:", flush=True)
                        run_command(f"tail -n 50 {DFX_LOG_FILE} | grep -i -E 'error|exception|fail'")
                    
                    run_command("dfx stop", check=False)
                    sys.exit(1)
                else:
                    print(f"test_{test_id}.run() function test passed!", flush=True)
                    print(f"Iteration {i} completed. Total entities inserted: {i * 100}", flush=True)
    
    finally:
        # Ensure dfx is always stopped at the end
        print("Stopping dfx...", flush=True)
        run_command("dfx stop", check=False)
        # Make sure all dfx processes are killed
        run_command("pkill -f dfx", check=False)
    
    print("All done!", flush=True)

if __name__ == "__main__":
    main()
