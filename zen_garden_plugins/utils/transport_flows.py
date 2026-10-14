"""Aggregate edge-based transport flows to the nodes they enter or leave."""

import xarray as xr
from linopy.expressions import LinearExpression


def nodal_transport_flows(
    model_constructor, technologies: list[str] | None = None
) -> tuple[LinearExpression, LinearExpression]:
    """Return the transport flows entering and leaving each node.

    Every edge has exactly one origin and one destination node, so the
    edge dimension of ``flow_transport`` can be grouped by either node without
    building a dense node-edge incidence matrix.

    Args:
        model_constructor: Active ZEN-garden model constructor.
        technologies: Transport technologies to include. All transport
            technologies are included if ``None``.

    Returns:
        Tuple ``(flow_in, flow_out)`` of linear expressions indexed by
        ``set_transport_technologies``, ``set_nodes`` and
        ``set_time_steps_operation``. ``flow_in`` is the flow on ingoing edges
        minus the transport losses, ``flow_out`` the flow on outgoing edges.
        Both are reindexed to all nodes; nodes without connected edges have no
        terms.
    """
    optimization_model = model_constructor.optimization_model
    network_topology = model_constructor.network_topology
    nodes = list(optimization_model.sets["set_nodes"])
    flow_transport = optimization_model.variables["flow_transport"].to_linexpr()
    flow_transport_loss = optimization_model.variables[
        "flow_transport_loss"
    ].to_linexpr()
    if technologies is not None:
        flow_transport = flow_transport.sel(set_transport_technologies=technologies)
        flow_transport_loss = flow_transport_loss.sel(
            set_transport_technologies=technologies
        )

    edges = list(flow_transport.coords["set_edges"].values)
    destination = {
        edge: node
        for node in nodes
        for edge in network_topology.calculate_connected_edges(node, "in")
    }
    origin = {
        edge: node
        for node in nodes
        for edge in network_topology.calculate_connected_edges(node, "out")
    }

    def edge_to_node(mapping):
        return xr.DataArray(
            [mapping[edge] for edge in edges],
            coords={"set_edges": edges},
            dims="set_edges",
            name="set_nodes",
        )

    flow_in = (
        (flow_transport - flow_transport_loss)
        .groupby(edge_to_node(destination))
        .sum()
        .reindex(set_nodes=nodes)
    )
    flow_out = (
        flow_transport.groupby(edge_to_node(origin)).sum().reindex(set_nodes=nodes)
    )
    return flow_in, flow_out
