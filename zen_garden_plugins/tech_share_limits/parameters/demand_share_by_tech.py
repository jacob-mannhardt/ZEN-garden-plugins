"""Bounds on the share of final demand covered by a conversion technology."""

from .tech_share_parameter import TechShareParameter


class DemandShareMaxByTech(TechShareParameter):
    """Maximum yearly share of a carrier's demand a technology may supply.

    Defaults to ``inf``, so the constraint is only added where a finite value
    is given.
    """

    name = "demand_share_max_by_tech"
    indices = (
        "set_conversion_technologies",
        "set_output_carriers",
        "set_nodes",
        "set_years",
    )
    doc = (
        "Maximum yearly share of a carrier's final demand that a conversion "
        "technology may supply"
    )
    carrier_attribute = "output_carrier"
    default_value = "inf"


class DemandShareMinByTech(TechShareParameter):
    """Minimum yearly share of a carrier's demand a technology must supply.

    Defaults to ``0``, so the constraint is only added where a positive value
    is given.
    """

    name = "demand_share_min_by_tech"
    indices = (
        "set_conversion_technologies",
        "set_output_carriers",
        "set_nodes",
        "set_years",
    )
    doc = (
        "Minimum yearly share of a carrier's final demand that a conversion "
        "technology must supply"
    )
    carrier_attribute = "output_carrier"
    default_value = 0
