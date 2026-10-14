"""Register components provided by ``transport_limit``.

ZEN-garden discovers this module through the ``zen_garden.plugins`` entry point
in ``pyproject.toml``. Importing the module registers the event handler below.
"""

from zen_garden import ConfigBase, Event, EventPublisher, ModelSchema

from zen_garden_plugins.transport_limit.constraints import TransportLimitConstraint
from zen_garden_plugins.transport_limit.parameters import (
    TransportLimitIn,
    TransportLimitOut,
)
from zen_garden_plugins.utils import add_components


class Config(ConfigBase):
    """Validate settings under ``plugins.transport_limit``.

    The plugin has no settings. Enable it in the configuration file with::

        plugins:
          transport_limit: {}
    """


@EventPublisher.register(Event.after_model_schema_creation)
def add_transport_limit_components(model_schema: ModelSchema) -> None:
    """Attach the transport limit parameters and constraint to the carriers.

    Args:
        model_schema: Mutable model blueprint supplied by ZEN-garden after its
            standard components have been registered.
    """
    add_components(
        model_schema,
        "Carrier",
        parameters=[TransportLimitIn, TransportLimitOut],
        constraints=[TransportLimitConstraint],
    )
