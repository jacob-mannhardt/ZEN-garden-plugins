"""Limit the annual transport flows into and out of each node.

The plugin adds the carrier parameters ``transport_limit_in`` and
``transport_limit_out`` and constrains the yearly sum of the transported flows
of each carrier entering and leaving each node. Each component lives in its own
subpackage, while :mod:`zen_garden_plugins.transport_limit.plugin` connects
them to the ZEN-garden model schema.
"""
