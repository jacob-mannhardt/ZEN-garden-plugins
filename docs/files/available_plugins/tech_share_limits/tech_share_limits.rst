.. _available_plugins.tech_share_limits:

Technology share limits
-----------------------

The ``tech_share_limits`` plugin bounds the yearly share that a conversion
technology has of a carrier. It is ported from the
`UB fork of ZEN-garden <https://github.com/UmikaB/ZEN-garden>`_ and adds two
families of linear constraints:

* **Share of final demand**: the yearly output of carrier :math:`c` from
  technology :math:`i` at node :math:`n` is bounded by a share of the yearly
  demand of :math:`c` at :math:`n`.
* **Share of conversion inflow**: the yearly input of carrier :math:`c` into
  technology :math:`i` at node :math:`n` is bounded by a share of the yearly
  input of :math:`c` into all conversion technologies at :math:`n`.

Enable the plugin in a ZEN-garden configuration as follows. Both constraint
families are enabled by default:

.. code-block:: yaml

   plugins:
     tech_share_limits:
       include_demand_share: true
       include_inflow_share: true

Parameters
^^^^^^^^^^

All parameters are dimensionless and indexed by conversion technology,
carrier, node, and year. They are inactive by default, so constraints are only
added where values are given.

.. list-table::
   :header-rows: 1

   * - Parameter
     - Carriers
     - Default
     - Constraint added where
   * - ``demand_share_max_by_tech``
     - output carriers
     - ``inf``
     - value is finite and demand is positive
   * - ``demand_share_min_by_tech``
     - output carriers
     - ``0``
     - value is positive and demand is positive
   * - ``inflow_share_max_by_tech``
     - input carriers
     - ``inf``
     - value is finite
   * - ``inflow_share_min_by_tech``
     - input carriers
     - ``0``
     - value is positive

Values are given in the technology folder, e.g.,
``set_conversion_technologies/heat_pump/demand_share_max_by_tech.csv``:

.. code-block:: text

   carrier,node,year,demand_share_max_by_tech
   heat,DE,2030,0.3
   heat,DE,2040,0.5

The ``carrier`` column may be omitted, in which case the values apply to all
input or output carriers of the technology. Years without values are
interpolated as for other yearly parameters. A default can also be set in
``attributes.yaml``:

.. code-block:: yaml

   demand_share_max_by_tech:
     default_value: inf
     unit: '1'

Note that the demand share relates the technology output to the demand at the
same node. Output that is transported to other nodes or stored still counts
towards the share.

Constraint definitions
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: zen_garden_plugins.tech_share_limits.constraints.TechShareOfFinalDemandConstraint
   :members: build

.. autoclass:: zen_garden_plugins.tech_share_limits.constraints.TechShareOfInflowConstraint
   :members: build

Module documentation
^^^^^^^^^^^^^^^^^^^^

.. automodule:: zen_garden_plugins.tech_share_limits.plugin
   :members:
   :undoc-members:
