"""Parameters supplied by ``tech_share_limits``."""

from .demand_share_by_tech import DemandShareMaxByTech, DemandShareMinByTech
from .input_share_by_tech import InputShareMaxByTech, InputShareMinByTech

__all__ = [
    "DemandShareMaxByTech",
    "DemandShareMinByTech",
    "InputShareMaxByTech",
    "InputShareMinByTech",
]
