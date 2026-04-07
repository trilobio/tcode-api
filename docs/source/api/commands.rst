Commands
==============

Commands are the data structures that you send to your fleet as instructions.

A T-code script is a list of commands, typically beginning with a chunk of ``ADD_***`` commands to define the entities that will be used in the script, then followed by various action commands to manipulate those entities.

.. tip::
  :collapsible: closed

  An important concept to understand before diving into T-code commands is the ``ValueWithUnits`` class, used in many of the following commands to represent physical quantities such as distances, speeds, and volumes.

  See :doc:`common` for full documentation of ``ValueWithUnits`` and related types.

.. automodule:: tcode_api.schemas.commands
   :members:
