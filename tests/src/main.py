from kybra import StableBTreeMap, ic, query, update, void

from kybra_simple_db import *
from tests import (
    test_audit,
    test_database,
    test_entity,
    test_example_1,
    test_example_2,
    test_mixins,
    test_performance,
    test_properties,
    test_relationships,
    test_upgrade_after,
    test_upgrade_before,
)

db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100, max_value_size=1_000
)
db_audit = StableBTreeMap[str, str](
    memory_id=1, max_key_size=100, max_value_size=1_000
)

Database.init(audit_enabled=False, db_storage=db_storage, db_audit=db_audit)


@update
def run_test(module_name: str) -> int:
    ic.print(f"Running test_{module_name}...")
    return globals()[f"test_{module_name}"].run()

@query
def dump_json() -> str:
    return Database.get_instance().raw_dump_json()


# Performance-specific entrypoints

@update
def disable_audit() -> void:
    Database.get_instance()._audit_enabled = False


@update
def insert_records(num_records: int) -> int:
    ic.print(f"Inserting {num_records} records...")
    return test_performance.insert_0(num_records)


@update
def read_records(from_id: int, to_id: int) -> int:
    ic.print(f"Reading {to_id - from_id} records...")
    return test_performance.read(from_id=from_id, to_id=to_id)


@query
def get_record(record_num: int) -> str:
    ic.print(f"Getting record {record_num}...")
    return test_performance.get_record_as_dict(record_num)


@query
def status() -> str:
    return str(Database.get_instance().status())
