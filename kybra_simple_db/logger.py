def running_on_ic() -> bool:
    try:
        from kybra import ic

        ic.print("running_on_ic: Running on IC")
        return True
    except ImportError:
        print("running_on_ic:Not running on IC")
    return False


def get_logger():
    if running_on_ic():
        from kybra import ic

        return lambda *args: ic.print(", ".join(map(str, args)))
    else:
        return print
