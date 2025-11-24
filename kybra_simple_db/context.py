"""Context management for caller identity.

Note: This implementation uses a simple module-level variable instead of
contextvars.ContextVar for compatibility with the Internet Computer (Kybra)
environment, which does not support ContextVar.

This is safe because:
- IC canisters are single-threaded (no concurrent request handling)
- Each canister call is processed sequentially
- No thread safety is needed in the IC environment

Warning: This implementation is NOT thread-safe. Do not use in multi-threaded
environments outside of the Internet Computer.
"""

# Module-level storage for current caller ID
# IC-compatible: Simple variable since IC canisters are single-threaded
_current_caller: str = "system"


def get_caller_id() -> str:
    """Get the current caller ID.

    Returns:
        str: Current caller ID (defaults to 'system')
    """
    return _current_caller


def set_caller_id(caller_id: str) -> None:
    """Set the current caller ID.

    Args:
        caller_id: ID of the caller to set
    """
    global _current_caller
    _current_caller = caller_id
