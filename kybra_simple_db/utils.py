import traceback

def running_on_ic() -> bool:

    try:
        from kybra import ic
        ic.print("running_on_ic: Running on IC")
        ic.print(traceback.format_exc())
        from .db_engine import KybraStableBTreeMapFactory
        KybraStableBTreeMapFactory()("storage")
        KybraStableBTreeMapFactory()("audit")

        return True
    except:
        pass
    return False