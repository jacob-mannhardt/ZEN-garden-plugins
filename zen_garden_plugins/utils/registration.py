"""Attach plugin components to the element classes of the model schema."""

from zen_garden import ModelSchema


def add_components(
    model_schema: ModelSchema,
    element_type: str,
    parameters=(),
    variables=(),
    constraints=(),
) -> None:
    """Append parameters, variables, and constraints to an element class.

    The element classes in the model schema are the ZEN-garden classes
    themselves, so their component lists persist for the lifetime of the Python
    process. Components are therefore only appended if they are not yet
    registered, which keeps repeated runs in the same process (e.g., in tests or
    scenario loops) from constructing a component twice.

    Args:
        model_schema: Mutable model blueprint supplied by ZEN-garden.
        element_type: Key of the element class in
            ``model_schema.element_type_classes``, e.g. ``"Carrier"``.
        parameters: Parameter classes owned by the element class.
        variables: Variable classes constructed by the element class.
        constraints: Constraint classes constructed by the element class.
    """
    element_class = model_schema.element_type_classes[element_type]

    def append_once(components, new_components):
        for component in new_components:
            if component not in components:
                components.append(component)

    # a parameter is added to own_parameters (where its input is stored) and
    # parameters (the complete list processed by model construction)
    append_once(element_class.own_parameters, parameters)
    append_once(element_class.parameters, parameters)
    append_once(element_class.variables, variables)
    append_once(element_class.constraints, constraints)
