"""Add up the annual carbon emissions of each node."""

from zen_garden.model.component_types.constraint import GenericConstraint

from zen_garden_plugins.utils import nodal_transport_flows

PLUGIN_NAME = "carbon_emissions_annual_limit_nodal"


class CarbonEmissionsAnnualNodalConstraint(GenericConstraint):
    """Define the annual carbon emissions of each node."""

    @classmethod
    def build(cls, model_constructor) -> None:
        """Summary:
        Add up all carbon emissions from technologies and carriers of each node.

        Formulation:

        .. math::
            M_{n,y} = M_{n,y}^\\mathrm{tech} + M_{n,y}^\\mathrm{carrier}
            + m^{\\mathrm{stor}} \\sum_{t\\in\\mathcal{T}_y}\\Delta t_t
            \\sum_{h\\in\\mathcal{H}^{\\mathrm{trans}}_{\\mathrm{CO_2}}}
            \\left[\\sum_{e'\\in\\mathcal{E}^{\\mathrm{out}}_n}
            F^{\\mathrm{trans}}_{h,e',t}
            - \\sum_{e\\in\\mathcal{E}^{\\mathrm{in}}_n}
            (F^{\\mathrm{trans}}_{h,e,t}-F^{\\mathrm{loss}}_{h,e,t})\\right]

        Notation:

        :math:`M_{n,y}^\\mathrm{tech}`: carbon emissions from technologies at
        node :math:`n` in year :math:`y` (emissions of transport technologies
        on edges are not attributed to nodes)
        :math:`M_{n,y}^\\mathrm{carrier}`: carbon emissions from carriers at
        node :math:`n` in year :math:`y`
        :math:`m^{\\mathrm{stor}}`: carbon intensity of the carbon storage
        technology
        :math:`\\mathcal{H}^{\\mathrm{trans}}_{\\mathrm{CO_2}}`: transport
        technologies of the carbon carrier

        The last term attributes the carbon that a node exports for storage
        elsewhere to the exporting node. It is only added if the carbon carrier
        configured in the plugin settings exists and is transported.
        """
        optimization_model = model_constructor.optimization_model
        sets = optimization_model.sets
        variables = optimization_model.variables
        nodes = list(sets["set_nodes"])
        time_step_duration = cls.get_year_time_step_duration_array(model_constructor)

        term_carbon_emissions_carrier = (
            variables["carbon_emissions_carrier"] * time_step_duration
        ).sum(["set_carriers", "set_time_steps_operation"])
        term_carbon_emissions_technology = (
            (variables["carbon_emissions_technology"] * time_step_duration)
            .sum(["set_technologies", "set_time_steps_operation"])
            .sel(set_location=nodes)
            .rename(set_location="set_nodes")
        )
        lhs = (
            variables["carbon_emissions_annual_nodal"]
            - term_carbon_emissions_technology
            - term_carbon_emissions_carrier
        )

        term_carbon_transport = cls._get_carbon_transport_term(
            model_constructor, time_step_duration
        )
        if term_carbon_transport is not None:
            lhs = lhs - term_carbon_transport

        optimization_model.add_constraint(
            "constraint_carbon_emissions_annual_nodal", lhs == 0
        )

    @classmethod
    def _get_carbon_transport_term(cls, model_constructor, time_step_duration):
        """Return the emissions attributed to net carbon exports of each node.

        Returns ``None`` if carbon transport is disabled in the plugin settings,
        the carbon carrier is not modeled, or no transport technology
        transports it.
        """
        optimization_model = model_constructor.optimization_model
        sets = optimization_model.sets
        config = model_constructor.config.plugins[PLUGIN_NAME]
        carbon_carrier = config["carbon_carrier"]
        carbon_storage = config["carbon_storage_technology"]
        if not config["include_carbon_transport"]:
            return None
        if carbon_carrier not in sets["set_carriers"]:
            return None
        if optimization_model.variables["flow_transport"].size == 0:
            return None
        carbon_technologies = [
            tech
            for tech in sets["set_transport_technologies"]
            if carbon_carrier in sets["set_reference_carriers"][tech]
        ]
        if not carbon_technologies:
            return None
        if carbon_storage not in sets["set_conversion_technologies"]:
            raise ValueError(
                f"The carrier '{carbon_carrier}' is transported, so the set of "
                f"conversion technologies must contain '{carbon_storage}' to "
                "attribute the stored carbon to the exporting nodes. Change "
                f"'carbon_storage_technology' in the settings of plugin "
                f"'{PLUGIN_NAME}' or set 'include_carbon_transport: false'."
            )
        carbon_intensity_carbon_storage = (
            optimization_model.parameters.carbon_intensity_technology.sel(
                set_technologies=carbon_storage
            )
            .to_series()
            .dropna()
            .iloc[0]
        )
        flow_in, flow_out = nodal_transport_flows(
            model_constructor, carbon_technologies
        )
        net_export = (flow_out - flow_in).sum("set_transport_technologies")
        return (net_export * time_step_duration * carbon_intensity_carbon_storage).sum(
            "set_time_steps_operation"
        )
