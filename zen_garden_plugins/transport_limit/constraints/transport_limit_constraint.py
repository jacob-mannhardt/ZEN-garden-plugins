"""Limit the yearly transport flows of each carrier into and out of each node."""

import numpy as np
import xarray as xr
from zen_garden.model.component_types.constraint import GenericConstraint

from zen_garden_plugins.utils import nodal_transport_flows


class TransportLimitConstraint(GenericConstraint):
    """Bound the yearly transported flow entering and leaving each node."""

    @classmethod
    def build(cls, model_constructor) -> None:
        """Summary:
        Yearly limit of the transported carrier flow into and out of each node.

        Formulation:

        .. math::
            \\sum_{t\\in\\mathcal{T}_y}\\Delta t_t
            \\sum_{h\\in\\mathcal{H}^{\\mathrm{trans}}_c}
            \\sum_{e\\in\\mathcal{E}^{\\mathrm{in}}_n}
            (F^{\\mathrm{trans}}_{h,e,t}-F^{\\mathrm{loss}}_{h,e,t})
            \\leq b^{\\mathrm{in}}_{c,n,y}

        .. math::
            \\sum_{t\\in\\mathcal{T}_y}\\Delta t_t
            \\sum_{h\\in\\mathcal{H}^{\\mathrm{trans}}_c}
            \\sum_{e'\\in\\mathcal{E}^{\\mathrm{out}}_n}
            F^{\\mathrm{trans}}_{h,e',t}
            \\leq b^{\\mathrm{out}}_{c,n,y}

        Notation:

        :math:`\\mathcal{H}^{\\mathrm{trans}}_c`: transport technologies with
        reference carrier :math:`c`
        :math:`F^{\\mathrm{trans}}_{h,e,t}`: transported flow on ingoing edge
        :math:`e`, minus loss :math:`F^{\\mathrm{loss}}_{h,e,t}`
        :math:`F^{\\mathrm{trans}}_{h,e',t}`: transported flow on outgoing edge
        :math:`e'`
        :math:`b^{\\mathrm{in}}_{c,n,y}`: transport limit into node :math:`n`
        :math:`b^{\\mathrm{out}}_{c,n,y}`: transport limit out of node :math:`n`

        Only finite limits are constrained.
        """
        optimization_model = model_constructor.optimization_model
        if optimization_model.variables["flow_transport"].size == 0:
            return
        transport_technologies = list(
            optimization_model.sets["set_transport_technologies"]
        )
        reference_carriers = optimization_model.sets["set_reference_carriers"]
        transport_limit_in = getattr(
            optimization_model.parameters, f"transport_limit_in"
        )
        transport_limit_out = getattr(
            optimization_model.parameters, f"transport_limit_out"
        )
        has_finite_limit = (transport_limit_in != np.inf) | (
            transport_limit_out != np.inf
        )
        other_dims = [d for d in has_finite_limit.dims if d != "set_carriers"]
        limited_carriers = has_finite_limit.any(other_dims)
        limited_technologies = [
            tech
            for tech in transport_technologies
            if limited_carriers.sel(set_carriers=reference_carriers[tech][0]).item()
        ]
        carrier_of_technology = xr.DataArray(
            [reference_carriers[tech][0] for tech in limited_technologies],
            coords={"set_transport_technologies": limited_technologies},
            dims="set_transport_technologies",
            name="set_carriers",
        )
        flow_in, flow_out = nodal_transport_flows(
            model_constructor, limited_technologies)

        for direction, flow in (("in", flow_in), ("out", flow_out)):
            # sum over all technologies of a carrier and all time steps of a year
            lhs = (
                flow.groupby(carrier_of_technology).sum()
                * cls.get_year_time_step_duration_array(model_constructor)
            ).sum("set_time_steps_operation")
            if direction == "in":
                transport_limit = transport_limit_in
            else:
                transport_limit = transport_limit_out
            transport_limit = xr.align(transport_limit, lhs.const, join="right")[0]
            mask = transport_limit != np.inf
            constraints = lhs.where(mask) <= transport_limit.where(mask, 0.0)
            optimization_model.add_constraint(
                f"constraint_transport_limit_{direction}", constraints
            )
