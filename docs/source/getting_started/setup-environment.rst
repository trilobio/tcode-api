Set Up Your Python Environment
==============================

The first step of python development is... developing your python environment. Let's get 'er done.

Prerequisites
-------------
- Python3.11 or higher

.. note::
  We're assuming that you have python 3.11 or higher installed on your computer.
   - If you're developing on a Trilobio Fleet Controller, this will be taken care of for you.
   - If you're developing on your local machine, please install python 3.11 or higher using your
     preferred method (We like managing our python versions with ``uv``).

Create a uv Application Project
-------------------------------
**Reference:** https://docs.astral.sh/uv/concepts/projects/init/

1. Make a new folder, inside of which you will write your TCode scripts. In the example below,
   I make a new folder called ``tcode-workspace/`` inside of the home directory. You can create this
   folder in a different location (ex. ``Desktop/``, or ``Documents/``) if you choose.

.. code-block:: bash

  cd ~/
  mkdir tcode-workspace

2. Enter that folder and initialize a ``uv`` project using the following commands:

.. code-block:: bash

   cd tcode-workspace
   uv init

3. Inspect the results.

- You should have seen the following response: ``Initialized project `tcode-workspace```.
- When you run the ``ls`` command to see what files were created, you'll see three files:

  - ``main.py``: A placeholder script that we will remove later.
  - ``pyproject.toml``: Environment dependencies and meta-information about your project.
  - ``README.md``: A placeholder file for documentation of your application.


Install ``tcode-api``
---------------------
**Reference:** https://docs.astral.sh/uv/concepts/projects/dependencies/#git

Now, we'll install ``tcode-api`` from GitHub into this newly created environment. From inside
your project folder, run the following command:

.. code-block:: bash

   uv add git+https://github.com/trilobio/tcode-api.git

Running this command should print out a list of dependencies installed by ``uv`` to support
``tcode-api``, as well as a line that looks similarly to this:

.. code-block:: bash

  Built tcode-api @ git+https://github.com/trilobio/tcode-api.git@0d51d10d00b5661867971b1e7eb9e6611eabd276

Now, you have a ``uv`` environment with tcode-api installed, and can get to coding!

Test Your Environment
---------------------
**Reference:** https://docs.astral.sh/uv/reference/cli/#uv-run

To verify that the environment is working correctly, let's spin up a Python shell and try to
import ``tcode-api``.

1. Start a Python shell inside your ``uv`` environment by running the following command:

.. code-block:: bash

   uv run python

2. Inside the Python shell, try to import ``tcode-api`` by running the following command:

.. code-block:: python

   from tcode_api import api as tc

3. If you don't see any error messages, congratulations! You've successfully set up your Python
environment for TCode development.
