Entities
========

Entities are the core objects that can be referenced in TCode commands. This includes tools, robots, labware, and more.

Entities have up to three actions associated with them: Creation, Deletion and Resolution.

Entity Creation
---------------

``CREATE_***`` TCode commands manipulate the robot state. For example, suppose you want a biologist to add a specific labware to a robot's deck. Here, you would use ``CREATE_LABWARE``. If you want a biologist to remove a labware from a fleet, you would use ``DELETE_LABWARE``.

.. note::
    Currently, only ``CREATE_LABWARE`` is implemented. Tools and robots are created when your fleet controller starts up, and pipette tips are implicitly created when you call ``CREATE_LABWARE`` with a ``PipetteTipRack`` description, and ``full=True``.

**Relevant TCode Commands**

  - :py:class:`tcode_api.api.commands.CREATE_LABWARE`

Entity Reference
----------------
``ADD_***`` TCode commands pair an entity with a identifier, so that you can reference that entity in later commands. For example, calling ``ADD_LABWARE(id_a, ...)`` allows you to use ``id_a`` in later commands such as ``PICK_UP_LABWARE(***, id_a)``. For more details, see :doc:`../concepts/entity_resolution`.

**Relevant TCode Commands**

  - :py:class:`tcode_api.api.commands.ADD_LABWARE`
  - :py:class:`tcode_api.api.commands.ADD_ROBOT`
  - :py:class:`tcode_api.api.commands.ADD_TOOL`
  - :py:class:`tcode_api.api.commands.ADD_PIPETTE_TIP_GROUP`


Documentation
-------------
.. automodule:: tcode_api.api.entity
   :members:
   :member-order: bysource
