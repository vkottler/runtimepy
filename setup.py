# =====================================
# generator=datazen
# version=3.2.0
# hash=23791ff25e92caf639fdcfe48ce010bf
# =====================================

"""
runtimepy - Package definition for distribution.
"""

# third-party
try:
    from setuptools_wrapper.setup import setup
except (ImportError, ModuleNotFoundError):
    from runtimepy_bootstrap.setup import setup  # type: ignore

# internal
from runtimepy import DESCRIPTION, PKG_NAME, VERSION

author_info = {
    "name": "Libre Embedded",
    "email": "vaughn@libre-embedded.com",
    "username": "libre-embedded",
}
pkg_info = {
    "name": PKG_NAME,
    "slug": PKG_NAME.replace("-", "_"),
    "version": VERSION,
    "description": DESCRIPTION,
    "versions": [
        "3.12",
        "3.13",
    ],
}
setup(
    pkg_info,
    author_info,
)
