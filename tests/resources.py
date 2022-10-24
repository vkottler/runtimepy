"""
A module for working with test data.
"""

# built-in
from pathlib import Path

# third-party
import pkg_resources
from vcorelib.paths import Pathlike, normalize


def resource(name: Pathlike, valid: bool = True, pkg: str = __name__) -> Path:
    """Locate the path to a test resource."""

    valid_str = "valid" if valid else "invalid"
    resource_path = Path("data", valid_str, normalize(name))
    return Path(pkg_resources.resource_filename(pkg, str(resource_path)))
