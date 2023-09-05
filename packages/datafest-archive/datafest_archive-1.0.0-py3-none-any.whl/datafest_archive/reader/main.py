from enum import Enum


class Reader(str, Enum):
    """The type of reader to use."""

    json = "json"
    sqlite = "sqlite"
