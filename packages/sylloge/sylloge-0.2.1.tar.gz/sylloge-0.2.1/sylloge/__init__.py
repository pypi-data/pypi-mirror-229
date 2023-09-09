import logging
from importlib.metadata import version  # pragma: no cover

from .base import EADataset
from .id_mapped import IdMappedEADataset
from .moviegraph_benchmark_loader import MovieGraphBenchmark
from .oaei_loader import OAEI
from .open_ea_loader import OpenEA

__all__ = [
    "OpenEA",
    "MovieGraphBenchmark",
    "OAEI",
    "IdMappedEADataset",
    "EADataset",
]
__version__ = version(__package__)
logging.getLogger(__name__).setLevel(logging.INFO)
