from kybra import StableBTreeMap, ic, query, update

from kybra_simple_db import *
from tests import (
    test_audit,
    test_benchmarks,
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
