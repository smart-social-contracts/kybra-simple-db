from kybra import StableBTreeMap, ic, query, update

from kybra_simple_db import *
from tests import (
    test_audit,
    test_database,
    test_entity,
    test_example_1,
    test_example_2,
    test_mixins,
    test_properties,
    test_relationships,
    test_stress_bulk_insert,
    test_stress_bulk_load,
    test_upgrade_after,
    test_upgrade_before,
)

db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100_000, max_value_size=1_000_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100_000, max_value_size=1_000_000
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)


@update
def run_test(module_name: str) -> int:
    ic.print(f"Running test_{module_name}...")
    return globals()[f"test_{module_name}"].run()


@query
def dump_json() -> str:
    return Database.get_instance().raw_dump_json()


@update
def execute_code(code: str) -> str:
    """Executes Python code and returns the output.

    This is the core function needed for the Kybra Simple Shell to work.
    It captures stdout, stderr, and return values from the executed code.
    """
    import io
    import sys
    import traceback

    stdout = io.StringIO()
    stderr = io.StringIO()
    sys.stdout = stdout
    sys.stderr = stderr

    try:
        # Try to evaluate as an expression
        result = eval(code, globals())
        if result is not None:
            ic.print(repr(result))
    except SyntaxError:
        try:
            # If it's not an expression, execute it as a statement
            # Use the built-in exec function but with a different name to avoid conflict
            exec_builtin = exec
            exec_builtin(code, globals())
        except Exception:
            traceback.print_exc()
    except Exception:
        traceback.print_exc()

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    return stdout.getvalue() + stderr.getvalue()
