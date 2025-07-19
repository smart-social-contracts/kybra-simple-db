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
    test_stress,
    test_upgrade_after,
    test_upgrade_before,
)

# Unique memory IDs for stable storage isolation
DB_STORAGE_MEMORY_ID = 0  # Main database storage
DB_AUDIT_MEMORY_ID = 1    # Audit log storage

# Size limits for stable storage maps
DB_MAX_KEY_SIZE = 100     # Maximum key size in bytes
DB_MAX_VALUE_SIZE = 2048  # Maximum value size in bytes (2KB)

db_storage = StableBTreeMap[str, str](
    memory_id=DB_STORAGE_MEMORY_ID,
    max_key_size=DB_MAX_KEY_SIZE,
    max_value_size=DB_MAX_VALUE_SIZE,
)

db_audit = StableBTreeMap[str, str](
    memory_id=DB_AUDIT_MEMORY_ID,
    max_key_size=DB_MAX_KEY_SIZE,
    max_value_size=DB_MAX_VALUE_SIZE,
)

Database.init(audit_enabled=True, db_storage=db_storage, db_audit=db_audit)


@update
def run_test(module_name: str, test_name: str = None, test_var: str = None) -> int:
    ic.print(
        f"Running test_{module_name}, test_name = {test_name}, test_var = {test_var}"
    )
    return globals()[f"test_{module_name}"].run(test_name, test_var)


@query
def dump_json() -> str:
    return Database.get_instance().raw_dump_json()
