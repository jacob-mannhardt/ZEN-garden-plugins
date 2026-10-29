"""Bounds on the share of a carrier's conversion inflow used by a technology."""

from .tech_share_parameter import TechShareParameter


class InflowShareMaxByTech(TechShareParameter):
    """Maximum yearly share of a carrier's inflow a technology may consume.

    Defaults to ``inf``, so the constraint is only added where a finite value
    is given.
    """

    name = "inflow_share_max_by_tech"
    indices = (
        "set_conversion_technologies",
        "set_input_carriers",
        "set_nodes",
        "set_years",
    )
    doc = (
        "Maximum yearly share of a carrier's total conversion inflow that a "
        "conversion technology may consume"
    )
    carrier_attribute = "input_carrier"
    default_value = "inf"


class InflowShareMinByTech(TechShareParameter):
    """Minimum yearly share of a carrier's inflow a technology must consume.

    Defaults to ``0``, so the constraint is only added where a positive value
    is given.
    """

    name = "inflow_share_min_by_tech"
    indices = (
        "set_conversion_technologies",
        "set_input_carriers",
        "set_nodes",
        "set_years",
    )
    doc = (
        "Minimum yearly share of a carrier's total conversion inflow that a "
        "conversion technology must consume"
    )
    carrier_attribute = "input_carrier"
    default_value = 0
