"""Parameters supplied by ``tech_share_limits``."""

from .demand_share_by_tech import DemandShareMaxByTech, DemandShareMinByTech
from .inflow_share_by_tech import InflowShareMaxByTech, InflowShareMinByTech

__all__ = [
    "DemandShareMaxByTech",
    "DemandShareMinByTech",
    "InflowShareMaxByTech",
    "InflowShareMinByTech",
]
