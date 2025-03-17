"""Tests that verify the example scripts run correctly."""

import os
import subprocess
import sys


def run_example(script_name: str) -> None:
    """Run an example script and verify it executes without error.

    Args:
        script_name: Name of the script to run (e.g. test_1.py)
    """
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    result = subprocess.run(
        [sys.executable, script_path], capture_output=True, text=True, check=False
    )
    assert (
        result.returncode == 0
    ), f"Example {script_name} failed with error:\n{result.stderr}"


def test_example_1():
    """Test that example 1 runs successfully."""
    run_example("test_1.py")


def test_example_2():
    """Test that example 2 runs successfully."""
    run_example("test_2.py")


def test_example_3():
    """Test that example 3 runs successfully."""
    run_example("test_3.py")
