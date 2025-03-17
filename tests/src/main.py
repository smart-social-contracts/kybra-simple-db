from kybra import query
from kybra_simple_db import *


@query
def greet() -> str:
    return "Hello!"


@query
def test1() -> str:
    return "Test 1"
