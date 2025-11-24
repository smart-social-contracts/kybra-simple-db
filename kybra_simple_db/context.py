"""Context management for caller identity."""

from contextvars import ContextVar

# Thread-safe storage for current caller ID
_current_caller: ContextVar[str] = ContextVar("current_caller", default="system")


def get_caller_id() -> str:
    """Get the current caller ID.

    Returns:
        str: Current caller ID (defaults to 'system')
    """
    return _current_caller.get()


def set_caller_id(caller_id: str) -> None:
    """Set the current caller ID.

    Args:
        caller_id: ID of the caller to set
    """
    _current_caller.set(caller_id)
