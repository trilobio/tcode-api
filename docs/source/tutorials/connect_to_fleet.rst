Tutorial: Connecting to a Trilobio Fleet
========================================

**Goal**: Connect to a Trilobio robot and jog it around.

Background
----------

In this tutorial, you will send jog commands to a robot in a Trilobot fleet using the python wrapper for the TCode API.

This tutorial assumes that:
   - A trilobot fleet is booted up
   - You are on the fleet control computer

A basic understanding of Python is also assumed.

Step 1: Connect to Fleet
------------------------

.. doctest:: connect_to_fleet

  >>> from tcode_api.servicer import TCodeServicerClient
  >>> client = TCodeServicerClient()
  >>> status = client.get_status()
  >>> print(status)
  GetStatusResponse(command_id=None, operation_count=0, run_state=False, result=Result(success=True, code='success', message=None, details=None))

The program that reads TCode and turns it into robot commands is called the "TCode Servicer". It runs on the fleet control computer. We will use the `TCodeServicerClient` class to connect to this program and talk to it.
The first two lines create the client.

.. note::

   Note that the TCodeServicerClient constructor is called with no arguments. By default, it connects to the TCode Servicer running on the local machine. If you are running this code on a different machine, look at the
   API documentation for how to specify the IP address and port of the target TCode Servicer.

.. code-block:: python

  from tcode_api.servicer import TCodeServicerClient
  client = TCodeServicerClient()

The third line calls the `get_status` method to check that we are connected. In the response object, we can see a lot of information that will be useful later.

.. code-block:: python

  status = client.get_status()
  print(status)

Step 2: Select a Robot
----------------------

Now that we've successfully retrieved the fleet status, we are ready to select a robot to control! Let's first tell the TCode servicer to find a robot on the fleet.

.. doctest:: connect_to_fleet

   import tcode_api.api as tc

   commands = []
   client.schedule_commands(commands)
