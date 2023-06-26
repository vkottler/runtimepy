# =====================================
# generator=datazen
# version=3.1.2
# hash=6701839983d2292671c1f49f66c938ae
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
    "name": "Vaughn Kottler",
    "email": "vaughnkottler@gmail.com",
    "username": "vkottler",
}
pkg_info = {
    "name": PKG_NAME,
    "slug": PKG_NAME.replace("-", "_"),
    "version": VERSION,
    "description": DESCRIPTION,
    "versions": [
        "3.8",
        "3.9",
        "3.10",
        "3.11",
    ],
}
setup(
    pkg_info,
    author_info,
)
