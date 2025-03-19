from kybra import StableBTreeMap

from .db_engine import manage_databases

default_storage_db = StableBTreeMap[str, str](
    memory_id=9, max_key_size=100_000, max_value_size=1_000_000
)
default_audit_db = StableBTreeMap[str, str](
    memory_id=11, max_key_size=100_000, max_value_size=1_000_000
)
manage_databases(default_storage_db, default_audit_db)