from kybra import query, ic

from kybra_simple_db import *  # TODO
from tests import test_1, test_2, test_entity, test_audit, test_database, test_mixins, test_properties, test_relationships, test_storage

@query
def greet() -> str:
    ic.print("Hello!")
    return "Hello!"


@query
def run_test(module_name:str) -> int: 
    ic.print(f"Running test_{module_name}...")
    return globals()[f"test_{module_name}"].run()
