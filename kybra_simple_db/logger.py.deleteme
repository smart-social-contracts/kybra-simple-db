from .utils import running_on_ic
import logging

def get_logger(name: str = None):
    if running_on_ic():
        from kybra import ic

        return lambda *args: ic.print(", ".join(map(str, args)))
    else:
        logger = logging.getLogger(name or "kybra")
        return logger.debug
