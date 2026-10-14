.. _available_plugins.transport_limit:

Transport limit
---------------

The ``transport_limit`` plugin limits the yearly amount of a carrier that is
transported into and out of a node. It adds two carrier parameters and one
constraint:

* ``transport_limit_in``: yearly limit of the transported flow into a node,
  net of transport losses;
* ``transport_limit_out``: yearly limit of the transported flow out of a node;
* ``constraint_transport_limit_in`` and ``constraint_transport_limit_out``:
  the yearly sum of the flows of all transport technologies with the
  carrier as reference carrier is bounded by the respective limit.

Only finite limits are constrained. Both parameters default to ``inf`` with the
unit of ``availability_import_yearly`` and ``availability_export_yearly``,
respectively, so they do not need to be added to the ``attributes.yaml`` file
of a carrier. Unlike ``carbon_emissions_annual_limit``, the limits are not
scaled to the modeled fraction of the year (as for
``availability_import_yearly``).

Enable the plugin in a ZEN-garden configuration as follows:

.. code-block:: yaml

   plugins:
     transport_limit: {}

Node- and year-specific limits are supplied in
``set_carriers/<carrier>/transport_limit_in.csv`` and
``set_carriers/<carrier>/transport_limit_out.csv``:

.. code-block:: text

   node,year,transport_limit_in
   CH,2030,1000
   CH,2040,500

Constraint definition
^^^^^^^^^^^^^^^^^^^^^

.. literalinclude:: ../../../../zen_garden_plugins/transport_limit/constraints/transport_limit_constraint.py
   :language: python

Module documentation
^^^^^^^^^^^^^^^^^^^^

.. automodule:: zen_garden_plugins.transport_limit.plugin
   :members:
   :undoc-members:
