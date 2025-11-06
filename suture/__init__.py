"""
Suture: Self-healing multi-agent framework for web data extraction

Suture orchestrates specialized AI agents to reliably extract structured data
from difficult web sources, automatically adapting to website changes.
"""

__version__ = "0.1.0"

from suture.core.config import SutureConfig
from suture.core.scraper import Scraper

__all__ = [
    "SutureConfig",
    "Scraper",
    "__version__",
]
