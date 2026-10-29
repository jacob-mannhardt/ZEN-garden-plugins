"""Bound the share of final demand covered by a conversion technology."""

from .tech_share_constraint import TechShareConstraint


class TechShareOfFinalDemandConstraint(TechShareConstraint):
    """Limit the yearly output of a technology relative to the carrier demand."""

    @classmethod
    def build(cls, model_constructor) -> None:
        """Summary:
        Bounds the yearly output of a conversion technology as a share of the
        yearly final demand of the output carrier at the same node.

        Formulation:

        .. math::
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t G^\\mathrm{out}_{i,c,n,t}
            \\leq \\overline{\\alpha}_{i,c,n,y}
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t D_{c,n,t}

        .. math::
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t G^\\mathrm{out}_{i,c,n,t}
            \\geq \\underline{\\alpha}_{i,c,n,y}
            \\sum_{t\\in\\mathcal{T}_y} \\Delta t_t D_{c,n,t}

        Notation:

        - :math:`G^\\mathrm{out}_{i,c,n,t}`: output flow of carrier :math:`c`
          from technology :math:`i` at node :math:`n` in time step :math:`t`
        - :math:`D_{c,n,t}`: demand of carrier :math:`c` at node :math:`n`
        - :math:`\\overline{\\alpha}_{i,c,n,y}`,
          :math:`\\underline{\\alpha}_{i,c,n,y}`: maximum and minimum share
          (``demand_share_max``, ``demand_share_min``)

        The upper bound is only added where the maximum share is finite, the
        lower bound only where the minimum share is positive. Neither is added
        where the yearly demand is zero.
        """
        optimization_model = model_constructor.optimization_model
        if len(optimization_model.sets["set_conversion_technologies"]) == 0:
            return
        parameters = optimization_model.parameters
        times = cls.get_year_time_step_duration_array(model_constructor)
        annual_demand = (
            (parameters.demand * times)
            .sum("set_time_steps_operation")
            .rename({"set_carriers": "set_output_carriers"})
        )
        for name, share, is_lower_bound in (
            (
                "constraint_tech_share_of_final_demand_max",
                parameters.demand_share_max,
                False,
            ),
            (
                "constraint_tech_share_of_final_demand_min",
                parameters.demand_share_min,
                True,
            ),
        ):
            active_entries = cls.get_active_entries(
                share, "set_output_carriers", is_lower_bound
            )
            if active_entries is None:
                continue
            mask, selection = active_entries
            demand = annual_demand.sel(
                set_output_carriers=selection["set_output_carriers"]
            )
            mask = mask & (demand > 0)
            annual_output = (
                optimization_model.variables["flow_conversion_output"].sel(selection)
                * times
            ).sum("set_time_steps_operation")
            lhs = annual_output.where(mask) - (share.sel(selection) * demand).where(
                mask, 0
            )
            if is_lower_bound:
                constraints = lhs >= 0
            else:
                constraints = lhs <= 0
            optimization_model.add_constraint(name, constraints)
