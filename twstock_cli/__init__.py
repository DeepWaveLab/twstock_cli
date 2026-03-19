"""twstock-cli — Agent-friendly Taiwan stock market data tool."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("twstock-cli")
except PackageNotFoundError:
    __version__ = "0.0.0"
