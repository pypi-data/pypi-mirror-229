"""LG SDK interface"""

from .api import LGApi, get_all_slc_with_data
from .auth import LGAuth

__all__ = ["LGApi", "LGAuth", "get_all_slc_with_data"]
