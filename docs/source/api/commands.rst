Commands
==============

Commands are the data structures that you send to your fleet as instructions.

A TCode script is a list of commands, typically beginning with a chunk of ``ADD_***`` commands to define the entities that will be used in the script, then followed by various action commands to manipulate those entities.

.. tip::
  :collapsible: closed

  An important concept to understand before diving into TCode commands it the ``ValueWithUnits`` class, used in many of the following commands to represent physical quantities such as distances, speeds, and volumes.

  .. autopydantic_model:: tcode_api.api.core.ValueWithUnits

.. automodule:: tcode_api.api.commands
   :members:
