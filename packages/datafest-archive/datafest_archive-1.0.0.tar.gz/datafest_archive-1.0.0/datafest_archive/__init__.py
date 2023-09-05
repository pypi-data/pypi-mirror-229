# type: ignore[attr-defined]
"""DataFestArchive is a Python package designed to generate the DataFestArchive website from past versions of DataFest"""

import sys
from importlib import metadata as importlib_metadata


def get_version() -> str:
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
