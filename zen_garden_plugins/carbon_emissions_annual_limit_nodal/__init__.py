"""Limit the annual carbon emissions of each node.

The plugin adds the energy-system parameter
``carbon_emissions_annual_limit_nodal``, the variable
``carbon_emissions_annual_nodal`` and two constraints that compute the annual
carbon emissions of each node and bound them by the nodal limit. Each component
lives in its own subpackage, while
:mod:`zen_garden_plugins.carbon_emissions_annual_limit_nodal.plugin` connects
them to the ZEN-garden model schema.
"""
