"""Bound the annual carbon emissions of each node."""

import numpy as np
from zen_garden.model.component_types.constraint import GenericConstraint


class CarbonEmissionsAnnualLimitNodalConstraint(GenericConstraint):
    """Limit the annual carbon emissions of each node."""

    @classmethod
    def build(cls, model_constructor) -> None:
        """Summary:
        Time dependent carbon emissions limit of each node.

        Formulation:

        .. math::
            M_{n,y} \\leq \\overline{m}_{n,y}

        Notation:

        :math:`M_{n,y}`: annual carbon emissions of node :math:`n` in year
        :math:`y`
        :math:`\\overline{m}_{n,y}`: annual carbon emissions limit of node
        :math:`n` in year :math:`y`

        Only finite limits are constrained.
        """
        optimization_model = model_constructor.optimization_model
        limit = optimization_model.parameters.carbon_emissions_annual_limit_nodal
        mask = limit != np.inf
        lhs = optimization_model.variables["carbon_emissions_annual_nodal"].where(mask)
        rhs = limit.where(mask, 0.0)
        optimization_model.add_constraint(
            "constraint_carbon_emissions_annual_limit_nodal", lhs <= rhs
        )
