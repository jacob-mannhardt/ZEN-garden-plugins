"""Constraints supplied by ``tech_share_limits``."""

from .tech_share_of_final_demand_constraint import TechShareOfFinalDemandConstraint
from .tech_share_of_inflow_constraint import TechShareOfInflowConstraint

__all__ = ["TechShareOfFinalDemandConstraint", "TechShareOfInflowConstraint"]
