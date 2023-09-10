# https://py-pkgs.org/03-how-to-package-a-python
# publish: https://www.softwarepragmatism.com/publish-python-to-pypi-with-poetry
# read version from installed package
from importlib.metadata import version
__version__ = version("pycounts_fe")