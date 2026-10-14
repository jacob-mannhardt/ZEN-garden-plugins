"""Define the yearly transport limits into and out of each node."""

from zen_garden.model.component_types.parameter import GenericParameter


class TransportLimitIn(GenericParameter):
    """Yearly limit on the transported carrier flow into a node.

    Users may provide node- and year-specific data in
    ``set_carriers/<carrier>/transport_limit_in.csv`` with columns ``node``,
    ``year`` and ``transport_limit_in``. If neither the attributes file nor a
    CSV file specify the parameter, it defaults to ``inf`` (no limit) with the
    unit of ``availability_import_yearly``.
    """

    name = "transport_limit_in"
    indices = ("set_carriers", "set_nodes", "set_years")
    doc = "Parameter which specifies the yearly transport limit into the node"
    unit_category = {"energy_quantity": 1}
    default_value = "inf"
    default_unit = "availability_import_yearly"


class TransportLimitOut(GenericParameter):
    """Yearly limit on the transported carrier flow out of a node.

    Users may provide node- and year-specific data in
    ``set_carriers/<carrier>/transport_limit_out.csv`` with columns ``node``,
    ``year`` and ``transport_limit_out``. If neither the attributes file nor a
    CSV file specify the parameter, it defaults to ``inf`` (no limit) with the
    unit of ``availability_export_yearly``.
    """

    name = "transport_limit_out"
    indices = ("set_carriers", "set_nodes", "set_years")
    doc = "Parameter which specifies the yearly transport limit out of the node"
    unit_category = {"energy_quantity": 1}
    default_value = "inf"
    default_unit = "availability_export_yearly"
