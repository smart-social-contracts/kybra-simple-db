"""Tests for relationship properties in Kybra Simple DB."""

import hashlib, string

from kybra_simple_db import *


def random_string_from_seed(seed: int, length: int = 10) -> str:
    """Generate deterministic alphanumeric string from a seed"""
    chars = string.ascii_letters + string.digits
    hex_digest = hashlib.sha256(str(seed).encode()).hexdigest()
    # Map each hex character to our character set
    return ''.join(chars[int(c, 16) % len(chars)] for c in hex_digest[:length])

total_num_records = 0

class Record(Entity):
    data = String(max_length=1024)

def insert(num_records=100):
    global total_num_records
    for i in range(num_records):
        Record(_id=random_string_from_seed(i + total_num_records, 64), data=random_string_from_seed(i, 1024))
    total_num_records += num_records
    return total_num_records

def read(from_id=0, to_id=100):
    for i in range(from_id, to_id):
        Record[random_string_from_seed(i, 64)].data
    return to_id - from_id

if __name__ == "__main__":
    exit(insert())
