from kybra import StableBTreeMap, ic, query, update, void

from kybra_simple_db import *
from tests import test_performance

db_storage = StableBTreeMap[str, str](
    memory_id=0, max_key_size=100, max_value_size=1_000
)

Database.init(db_storage=db_storage)


@update
def run_test(module_name: str) -> int:
    ic.print(f"Running test_{module_name}...")
    return globals()[f"test_{module_name}"].run()


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
