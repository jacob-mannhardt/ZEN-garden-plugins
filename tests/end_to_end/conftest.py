import os
import sys

import pytest
from zen_garden import EventPublisher
from zen_garden.elements import ELEMENT_TYPE_CLASSES, EnergySystem

COMPONENT_LISTS = ("own_parameters", "parameters", "variables", "constraints")


@pytest.fixture(autouse=True)
def isolate_plugin_observers():
    """Prevent plugin event handlers from leaking between end-to-end tests.

    Plugin modules register their event handlers when they are imported. The
    cached modules are therefore removed as well, so that a plugin used by
    several tests registers its handlers again in each of them.
    """

    def reset():
        EventPublisher.deregister_all()
        for module_name in list(sys.modules):
            if module_name.startswith("zen_garden_plugins.") and module_name.endswith(
                ".plugin"
            ):
                del sys.modules[module_name]

    reset()
    yield
    reset()


@pytest.fixture(autouse=True)
def isolate_plugin_components():
    """Restore the element component lists that plugins extend in place."""
    element_classes = [EnergySystem, *ELEMENT_TYPE_CLASSES.values()]
    snapshot = {
        (element_class, name): list(getattr(element_class, name))
        for element_class in element_classes
        for name in COMPONENT_LISTS
    }
    yield
    for (element_class, name), components in snapshot.items():
        getattr(element_class, name)[:] = components


@pytest.fixture
def fixtures_path():
    """Return the path containing the standard end-to-end fixtures."""
    return os.path.join(os.path.dirname(__file__), "fixtures")
