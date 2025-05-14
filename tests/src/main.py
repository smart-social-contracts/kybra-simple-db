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
    test_upgrade_after,
    test_upgrade_before,
    test_performance,
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

@update
def insert_records(num_records: int) -> int:
    ic.print(f"Inserting {num_records} records...")
    return test_performance.insert(num_records)

@update
def read_records(from_id: int, to_id: int) -> int:
    ic.print(f"Reading {to_id - from_id} records...")
    return test_performance.read(from_id=from_id, to_id=to_id)

@query
def dump_json() -> str:
    return Database.get_instance().raw_dump_json()