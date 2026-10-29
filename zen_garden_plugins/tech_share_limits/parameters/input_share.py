"""Bounds on the share of a carrier's conversion input used by a technology."""

from .tech_share_parameter import TechShareParameter


class InputShareMax(TechShareParameter):
    """Maximum yearly share of a carrier's input a technology may consume.

    Defaults to ``inf``, so the constraint is only added where a finite value
    is given.
    """

    name = "input_share_max"
    indices = (
        "set_conversion_technologies",
        "set_input_carriers",
        "set_nodes",
        "set_years",
    )
    doc = (
        "Maximum yearly share of a carrier's total conversion input that a "
        "conversion technology may consume"
    )
    carrier_attribute = "input_carrier"
    default_value = "inf"


class InputShareMin(TechShareParameter):
    """Minimum yearly share of a carrier's input a technology must consume.

    Defaults to ``0``, so the constraint is only added where a positive value
    is given.
    """

    name = "input_share_min"
    indices = (
        "set_conversion_technologies",
        "set_input_carriers",
        "set_nodes",
        "set_years",
    )
    doc = (
        "Minimum yearly share of a carrier's total conversion input that a "
        "conversion technology must consume"
    )
    carrier_attribute = "input_carrier"
    default_value = 0
