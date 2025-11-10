from kybra import StableBTreeMap, ic, query, update

from kybra_simple_db import *
from tests import (
    test_alias_and_properties,
    test_audit,
    test_database,
    test_enhanced_relations,
    test_entity,
    test_example_1,
    test_example_2,
    test_mixins,
    test_namespaces,
    test_properties,
    test_relationships,
    test_serialization,
    test_stress,
    test_upgrade_after,
    test_upgrade_before,
)

# Unique memory IDs for stable storage isolation
# memory_id = 0  # Main database storage
# memory_id = 1  # Audit log storage
# Size limits for stable storage maps
# max_key_size = 100  # Maximum key size in bytes
# max_value_size = 2048  # Maximum value size in bytes (2KB)

db_storage = StableBTreeMap[str, str](
    memory_id=0,
    max_key_size=100,
    max_value_size=2048,
)

db_audit = StableBTreeMap[str, str](
    memory_id=1,
    max_key_size=100,
    max_value_size=2048,
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
