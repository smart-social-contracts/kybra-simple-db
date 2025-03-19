from kybra import ic, query, update, StableBTreeMap

from kybra_simple_db import *  # TODO
from tests import (
    test_example_1,
    test_example_2,
    test_audit,
    test_database,
    test_entity,
    test_mixins,
    test_properties,
    test_relationships,
    test_storage,
)

import kybra_simple_db.initialize


@query
def greet() -> str:
    ic.print("Hello!")
    return "Hello!"


@update
def run_test(module_name: str) -> int:
    ic.print(f"Running test_{module_name}...")

    # default_storage_db.insert('test', 'some_test')
    # ic.print(f"good")
    return globals()[f"test_{module_name}"].run()
