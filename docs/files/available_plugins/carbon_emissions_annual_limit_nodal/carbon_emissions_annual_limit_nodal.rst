.. _available_plugins.carbon_emissions_annual_limit_nodal:

Nodal annual carbon emissions limit
-----------------------------------

The ``carbon_emissions_annual_limit_nodal`` plugin computes the annual carbon
emissions of each node and limits them. It adds the following components to
the energy system:

* ``carbon_emissions_annual_limit_nodal``: annual carbon emissions limit of
  each node. Like ``carbon_emissions_annual_limit``, it refers to a full year
  and is scaled to the modeled fraction of the year;
* ``carbon_emissions_annual_nodal``: variable for the annual carbon emissions
  of each node;
* ``constraint_carbon_emissions_annual_nodal``: the nodal emissions are the
  sum of the carrier and technology emissions at the node. Emissions of
  transport technologies occur on edges and are not attributed to nodes;
* ``constraint_carbon_emissions_annual_limit_nodal``: the nodal emissions are
  bounded by the finite nodal limits.

If the model contains a carbon carrier that is transported, carbon that a node
exports for storage at another node is attributed to the exporting node: the
net carbon exports of each node are multiplied by the carbon intensity of the
carbon storage technology and added to its emissions. The names of the carbon
carrier and the carbon storage technology can be configured.

Enable the plugin in a ZEN-garden configuration as follows (the values shown
are the defaults):

.. code-block:: yaml

   plugins:
     carbon_emissions_annual_limit_nodal:
       include_carbon_transport: true
       carbon_carrier: carbon
       carbon_storage_technology: carbon_storage

The limit defaults to ``inf`` with the unit of
``carbon_emissions_annual_limit``. Node- and year-specific limits are
supplied in ``energy_system/carbon_emissions_annual_limit_nodal.csv``:

.. code-block:: text

   node,year,carbon_emissions_annual_limit_nodal
   DE,2030,0.2
   DE,2040,0.1

Constraint definitions
^^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../zen_garden_plugins/carbon_emissions_annual_limit_nodal/constraints/carbon_emissions_annual_nodal_constraint.py
   :language: python

.. literalinclude:: ../../../../zen_garden_plugins/carbon_emissions_annual_limit_nodal/constraints/carbon_emissions_annual_limit_nodal_constraint.py
   :language: python

Module documentation
^^^^^^^^^^^^^^^^^^^^

.. automodule:: zen_garden_plugins.carbon_emissions_annual_limit_nodal.plugin
   :members:
   :undoc-members:
