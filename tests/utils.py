import os
import subprocess


def run_command(command):
    """
    Run a shell command and return the output.

    Args:
        command: The command to run
    """

    # For normal commands, use subprocess with timeout
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True,
        bufsize=1,  # Line buffered
    )

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Error executing command: {stderr}")
        return None

    return stdout


# def print(message):
#     """Print a message and flush stdout immediately."""
#     print(message, flush=True)


def check_value(actual, expected, operator="=="):
    if operator == "==":
        if expected != actual:
            raise Exception(
                f"❌ Value mismatch: expected {expected} {operator} actual {actual}"
            )
    elif operator == "<":
        if expected >= actual:
            raise Exception(
                f"❌ Value mismatch: expected {expected} {operator} actual {actual}"
            )
    else:
        raise Exception(f"❌ Invalid operator: {operator}")

    print(f"✅ Value match: expected {expected} {operator} actual {actual}")
