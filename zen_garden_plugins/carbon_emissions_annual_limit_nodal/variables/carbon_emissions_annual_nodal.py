"""Define the annual carbon emissions of each node."""

from zen_garden.model.component_types.variable import GenericVariable


class CarbonEmissionsAnnualNodal(GenericVariable):
    """Variable for the annual carbon emissions of each node (unbounded)."""

    name = "carbon_emissions_annual_nodal"
    indices = ["set_nodes", "set_years"]
    doc = "Variable for annual carbon emissions of energy system for each node"
    unit_category = {"emissions": 1}
