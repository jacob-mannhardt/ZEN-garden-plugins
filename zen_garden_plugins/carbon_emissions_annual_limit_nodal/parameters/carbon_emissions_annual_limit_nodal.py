"""Define the annual carbon emissions limit of each node."""

from zen_garden.model.component_types.parameter import GenericParameter


class CarbonEmissionsAnnualLimitNodal(GenericParameter):
    """Annual carbon emissions limit of each node.

    Users may provide node- and year-specific data in
    ``energy_system/carbon_emissions_annual_limit_nodal.csv`` with columns
    ``node``, ``year`` and ``carbon_emissions_annual_limit_nodal``. If neither
    the attributes file nor a CSV file specify the parameter, it defaults to
    ``inf`` (no limit) with the unit of ``carbon_emissions_annual_limit``.

    Like ``carbon_emissions_annual_limit``, the limit refers to a full year and
    is scaled to the modeled fraction of the year.
    """

    name = "carbon_emissions_annual_limit_nodal"
    indices = ("set_nodes", "set_years")
    doc = "Parameter which specifies the annual carbon emissions limit of each node"
    unit_category = {"emissions": 1}
    default_value = "inf"
    default_unit = "carbon_emissions_annual_limit"

    @classmethod
    def get_model_data(cls, model_constructor, index_names: list[str]):
        """Select the modeled nodes and years and scale to the modeled year.

        The default energy-system implementation selects ``set_time_steps``
        on the first index level, which only works for parameters indexed by
        years alone. This parameter is therefore selected by the full
        ``(node, year)`` index of the current optimization step instead.
        """
        energy_system = model_constructor.energy_system
        custom_set, index_list = model_constructor.create_custom_set(index_names)
        component_data = getattr(energy_system, cls.name).loc[custom_set]
        fraction_year = (
            model_constructor.config.system.unaggregated_time_steps_per_year
            / model_constructor.config.system.total_hours_per_year
        )
        units = energy_system.units.get(cls.name, {})
        return component_data * fraction_year, index_list, units
