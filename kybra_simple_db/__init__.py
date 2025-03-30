"""
Kybra Simple DB - A lightweight key-value database with entity relationships and audit logging
"""

from kybra_simple_logging import get_logger
logger = get_logger('kybra_simple_db')

from .db_engine import Database
from .entity import Entity
from .mixins import TimestampedMixin
from .properties import (
    Boolean,
    Float,
    Integer,
    ManyToMany,
    ManyToOne,
    OneToMany,
    OneToOne,
    String,
)
from .storage import MemoryStorage, Storage
from .system_time import SystemTime
from .utils import running_on_ic

__version__ = "0.1.1"
__all__ = [
    "Database",
    "Entity",
    "Storage",
    "MemoryStorage",
    "TimestampedMixin",
    "String",
    "Integer",
    "Float",
    "Boolean",
    "OneToOne",
    "OneToMany",
    "ManyToOne",
    "ManyToMany",
    "SystemTime",
    "get_logger",
    "running_on_ic",
]
