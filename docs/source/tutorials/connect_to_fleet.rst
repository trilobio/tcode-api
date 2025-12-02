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

.. code-block:: python

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

.. code-block:: python

   import tcode_api.api as tc
   from tcode_api.utilities import generate_id()

   # Generate the TCode script
   robot_id = generate_id()
   commands = []
   commands.append(
     tc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor())
   )

   # Schedule the TCode script
   client.schedule_commands(commands)

   # Run the TCode script
   client.execute_run_loop()

This script demonstrates the three main steps to run a TCode script on your fleet:
  1. Generate a list of TCode commands
  2. Schedule the script with your fleet
  3. Execute the script on your fleet

Let's first look at step 1:
.. code-block:: python

  import tcode_api.api as tc
  from tcode_api.utilities import generate_id()
  from tcode_api.servicer import TCodeServicerClient

  client = TCodeServicerClient()

When writing TCode, the primary python data structures for commands, errors, data structures. etc. are stored within ``tcode_api.api``. We import this library as ``tc`` for shorthand.

In addition to the core API, ``tcode_api`` has a few helper functions to make writing TCode scripts in python easier. These functions are stored in ``tcode_api.utilities``. Here, we're importing
a function to generate unique identifiers for TCode entities.

The ``TCodeServicerClient`` code we've seen before, so let's move on.

.. code-block:: python
  
  robot_id = generate_id()

Next, we'll instantiate an id for the robot. Entities that are referenced by TCode commands are referenced by identifier, and identifiers are linked to "real objects" on your fleet through ``ADD_***`` commands.
Typically, your tcode generation code will have a block of ``generate_id()`` calls at the top to create ids for all of your relevant objects.

.. code-block:: python

   commands = []

This line instantiates an empty list to store TCode commands. We'll use ``append`` to serially write the script by adding commands to the end of this list.

Now: Let's add our first command!

.. code-block:: python

  commands.append(
    rc.ADD_ROBOT(id=robot_id, descriptor=tc.RobotDescriptor())
  )

This line appends our first command, ``tc.ADD_ROBOT``. Into this function, we pass our generated identifier, and a descriptor of a robot. Note that this descriptor has no attributes specified,
and so will match any robot in the fleet. If your fleet has only one robot, this is great. If your fleet has multiple robots, however, you must add more information to the descriptor to ensure
that you control the expected robot.

How do we know that this is good TCode? Let's ask the fleet, by calling the ``schedule_commands`` endpoint.

.. code-block:: python

   client.schedule_commands(commands)

This command will perform the following:
  1. Check that the TCode is valid
  2. Check that all of the entities resolve to valid "real-life" objects
  3. Schedule the commands.

Now, your robot has commands scheduled! All there is left to do is run the commands.

.. code-block:: python

   client.execute_run_loop()

The ``execute_run_loop()`` method is a bare-bones loop that monitors the fleet until it finished the script or raises an error. Internally, the basic logic looks similar to this snippet:

.. code-block:: python

   while True:
      try:
        time.sleep(0.1)  # Don't busy-wait
        status = client.get_status()

        # If we reached the end of the script, finish
        if status.operation_count == 0:
          client.set_run_state(False)
          return

        # If we hit an error, finish
        if not status.result.sucess:
          print(status.result.message)
          client.set_run_state(False)
          return

      # If we hit <Ctrl-C>, clear the robot & finish
      except KeyboardInterrupt:
        client.set_run_state(False)

        # Reset the robot state to empty deck, no commands
        client.clear_tcode_resolution()
        client.clear_labware()

With this interface, the function will run until the robot either finishes the script or hits an error, in which case it will print the error message, then stop. If you press <Ctrl-C>, the robot
will also stop.

Now, try out the script!
