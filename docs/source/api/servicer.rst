TCode Servicer API
------------------

The ``tcode_api.api`` submodule allows you to write tcode scripts, but how do you put them on the robot?

The ``tcode_api.servicer`` submodule provides a client interface and relevant data structures for running tcode scripts on a robot, as well as other common tasks such as pausing and querying current runstate.

.. autoclass:: tcode_api.servicer.client.TCodeServicerClient
    :members:
