from kybra import query, ic

from kybra_simple_db import *  # TODO
from tests import test_1

@query
def greet() -> str:
    ic.print("Hello!")
    return "Hello!"


@query
def run_test1() -> str: 
    ic.print("Running test 1...")
    return test_1.run()
