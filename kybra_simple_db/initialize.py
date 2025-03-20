
_running_on_ic = False

default_storage_db = None
default_audit_db = None

try:
    from kybra import StableBTreeMap

    default_storage_db = StableBTreeMap[str, str](
        memory_id=9, max_key_size=100_000, max_value_size=1_000_000
    )
    default_audit_db = StableBTreeMap[str, str](
        memory_id=11, max_key_size=100_000, max_value_size=1_000_000
    )
except:
    pass



