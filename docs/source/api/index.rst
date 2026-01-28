tcode-api API Reference
=======================

This section of the documentation covers the nitty-gritty of the various interfaces for the tcode-api package.

Let's dive into the details!

TCode API
---------

The core data structures in the ``tcode_api`` package are all exposed in the ``tcode_api.api`` submodule. All examples will use the following import alias for brevity:

.. code-block:: python

   import tcode_api.api as tc

.. toctree ::
   :maxdepth: 1

   commands
   entity
   labware
   locations

TCode Servicer API
------------------

The components that allow you runtime control of your fleet are exposed in the ``tcode_api.servicer`` submodule.

.. toctree ::
   :maxdepth: 1

   servicer

TCode Integrator API
--------------------

This API allows you to integrate with external devices in one direction

.. toctree::
    :maxdepth: 2

    integrator
