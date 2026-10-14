"""Register components provided by ``carbon_emissions_annual_limit_nodal``.

ZEN-garden discovers this module through the ``zen_garden.plugins`` entry point
in ``pyproject.toml``. Importing the module registers the event handler below.
"""

from pydantic import Field
from zen_garden import ConfigBase, Event, EventPublisher, ModelSchema

from zen_garden_plugins.carbon_emissions_annual_limit_nodal.constraints import (
    CarbonEmissionsAnnualLimitNodalConstraint,
    CarbonEmissionsAnnualNodalConstraint,
)
from zen_garden_plugins.carbon_emissions_annual_limit_nodal.parameters import (
    CarbonEmissionsAnnualLimitNodal,
)
from zen_garden_plugins.carbon_emissions_annual_limit_nodal.variables import (
    CarbonEmissionsAnnualNodal,
)
from zen_garden_plugins.utils import add_components


class Config(ConfigBase):
    """Validate settings under ``plugins.carbon_emissions_annual_limit_nodal``.

    Users may write the following in their configuration file::

        plugins:
          carbon_emissions_annual_limit_nodal:
            include_carbon_transport: true
            carbon_carrier: carbon
            carbon_storage_technology: carbon_storage
    """

    include_carbon_transport: bool = Field(
        default=True,
        description=(
            "Whether to attribute the emissions of carbon that is transported "
            "to and stored at another node to the exporting node."
        ),
    )
    carbon_carrier: str = Field(
        default="carbon",
        description="Name of the carrier representing captured carbon.",
    )
    carbon_storage_technology: str = Field(
        default="carbon_storage",
        description=(
            "Name of the conversion technology storing carbon. Its carbon "
            "intensity is applied to the net carbon exports of each node."
        ),
    )


@EventPublisher.register(Event.after_model_schema_creation)
def add_carbon_emissions_annual_limit_nodal_components(
    model_schema: ModelSchema,
) -> None:
    """Attach the nodal emissions components to the energy system.

    Args:
        model_schema: Mutable model blueprint supplied by ZEN-garden after its
            standard components have been registered.
    """
    add_components(
        model_schema,
        "EnergySystem",
        parameters=[CarbonEmissionsAnnualLimitNodal],
        variables=[CarbonEmissionsAnnualNodal],
        constraints=[
            CarbonEmissionsAnnualNodalConstraint,
            CarbonEmissionsAnnualLimitNodalConstraint,
        ],
    )
