"""Bound the share of a carrier's conversion inflow used by a technology."""

from .tech_share_constraint import TechShareConstraint


class TechShareOfInflowConstraint(TechShareConstraint):
    """Limit the yearly input of a technology relative to all conversion inputs."""

    @classmethod
    def build(cls, model_constructor) -> None:
        """Summary:
        Bounds the yearly input of a conversion technology as a share of the
        yearly input of the same carrier into all conversion technologies at
        the same node.

        Formulation:

        .. math::
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t G^\\mathrm{in}_{i,c,n,t}
            \\leq \\overline{\\beta}_{i,c,n,y}
            \\sum_{j\\in\\mathcal{I}} \\sum_{t\\in\\mathcal{T}_y}
            \\Delta t_t G^\\mathrm{in}_{j,c,n,t}

        .. math::
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t G^\\mathrm{in}_{i,c,n,t}
            \\geq \\underline{\\beta}_{i,c,n,y}
            \\sum_{j\\in\\mathcal{I}} \\sum_{t\\in\\mathcal{T}_y}
            \\Delta t_t G^\\mathrm{in}_{j,c,n,t}

        Notation:

        - :math:`G^\\mathrm{in}_{i,c,n,t}`: input flow of carrier :math:`c`
          into technology :math:`i` at node :math:`n` in time step :math:`t`
        - :math:`\\mathcal{I}`: set of conversion technologies
        - :math:`\\overline{\\beta}_{i,c,n,y}`,
          :math:`\\underline{\\beta}_{i,c,n,y}`: maximum and minimum share
          (``inflow_share_max_by_tech``, ``inflow_share_min_by_tech``)

        The upper bound is only added where the maximum share is finite, the
        lower bound only where the minimum share is positive.
        """
        optimization_model = model_constructor.optimization_model
        if len(optimization_model.sets["set_conversion_technologies"]) == 0:
            return
        parameters = optimization_model.parameters
        times = cls.get_year_time_step_duration_array(model_constructor)
        for name, share, is_lower_bound in (
            (
                "constraint_tech_share_of_inflow_max",
                parameters.inflow_share_max_by_tech,
                False,
            ),
            (
                "constraint_tech_share_of_inflow_min",
                parameters.inflow_share_min_by_tech,
                True,
            ),
        ):
            active_entries = cls.get_active_entries(
                share, "set_input_carriers", is_lower_bound
            )
            if active_entries is None:
                continue
            mask, selection = active_entries
            annual_input = (
                optimization_model.variables["flow_conversion_input"].sel(
                    set_input_carriers=selection["set_input_carriers"]
                )
                * times
            ).sum("set_time_steps_operation")
            total_input = annual_input.sum("set_conversion_technologies")
            lhs = (
                annual_input.sel(
                    set_conversion_technologies=selection["set_conversion_technologies"]
                )
                - share.sel(selection).where(mask, 0) * total_input
            ).where(mask)
            if is_lower_bound:
                constraints = lhs >= 0
            else:
                constraints = lhs <= 0
            optimization_model.add_constraint(name, constraints)
