"""Register components provided by ``tech_share_limits``.

ZEN-garden discovers this module through the ``zen_garden.plugins`` entry point
in ``pyproject.toml``. Importing the module registers the event handler below,
which attaches the share parameters and constraints to the conversion
technologies before input data is read and the optimization model is
constructed.
"""

from pydantic import Field
from zen_garden import ConfigBase, Event, EventPublisher, ModelSchema
from zen_garden.elements.conversion_technology import ConversionTechnology
from zen_garden.model.component_types.constraint import GenericConstraint
from zen_garden.model.component_types.parameter import GenericParameter

from zen_garden_plugins.tech_share_limits.constraints import (
    TechShareOfFinalDemandConstraint,
    TechShareOfInflowConstraint,
)
from zen_garden_plugins.tech_share_limits.parameters import (
    DemandShareMaxByTech,
    DemandShareMinByTech,
    InflowShareMaxByTech,
    InflowShareMinByTech,
)


class Config(ConfigBase):
    """Validate settings under ``plugins.tech_share_limits``.

    Both constraint families are enabled by default::

        plugins:
          tech_share_limits:
            include_demand_share: true
            include_inflow_share: true
    """

    include_demand_share: bool = Field(
        default=True,
        description=(
            "Whether to bound the share of final demand covered by a "
            "conversion technology."
        ),
    )
    include_inflow_share: bool = Field(
        default=True,
        description=(
            "Whether to bound the share of a carrier's conversion inflow used "
            "by a conversion technology."
        ),
    )


def _append_missing(target: list, components: list) -> None:
    """Append components to ``target`` that are not yet contained in it."""
    target.extend(c for c in components if c not in target)


@EventPublisher.register(Event.after_model_schema_creation)
def add_tech_share_limits(model_schema: ModelSchema) -> None:
    """Attach the share parameters and constraints to conversion technologies.

    The parameters are added to ``own_parameters`` of the conversion
    technology, which declares where they are built. They are also added to
    ``parameters`` of the conversion technology and all of its subclasses
    (e.g., retrofitting technologies), because subclasses compose that list
    when they are defined and every conversion technology needs the input data.

    Args:
        model_schema: Mutable model blueprint supplied by ZEN-garden after its
            standard components have been registered.
    """
    config = model_schema.config.plugins["tech_share_limits"]
    parameters: list[type[GenericParameter]] = []
    constraints: list[type[GenericConstraint]] = []
    if config["include_demand_share"]:
        parameters.extend([DemandShareMaxByTech, DemandShareMinByTech])
        constraints.append(TechShareOfFinalDemandConstraint)
    if config["include_inflow_share"]:
        parameters.extend([InflowShareMaxByTech, InflowShareMinByTech])
        constraints.append(TechShareOfInflowConstraint)

    conversion_technology = model_schema.element_type_classes["ConversionTechnology"]
    if not issubclass(conversion_technology, ConversionTechnology):
        raise TypeError(
            "Expected the 'ConversionTechnology' schema entry to contain a "
            "ConversionTechnology subclass"
        )
    _append_missing(conversion_technology.own_parameters, parameters)
    _append_missing(conversion_technology.constraints, constraints)
    for element_class in model_schema.element_type_classes.values():
        if issubclass(element_class, ConversionTechnology):
            _append_missing(element_class.parameters, parameters)
