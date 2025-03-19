from kybra import ic, query, update, StableBTreeMap

# from kybra_simple_db import *  # TODO
# from tests import (
#     test_example_1,
#     test_example_2,
#     test_audit,
#     test_database,
#     test_entity,
#     test_mixins,
#     test_properties,
#     test_relationships,
#     test_storage,
# )


@query
def greet() -> str:
    ic.print("Hello!")
    return "Hello!"


@update
def run_test(module_name: str) -> int:
    ic.print(f"Running test_{module_name}...")
    
    my_map = StableBTreeMap[str, str](
        memory_id=9, max_key_size=100_000, max_value_size=1_000_000
    )

    my_map.insert('my_key', 'my_value')
    ic.print(my_map.get('my_key'))

    return "OK"
    #return globals()[f"test_{module_name}"].run()
