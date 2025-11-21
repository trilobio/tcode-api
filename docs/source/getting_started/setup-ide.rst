Set Up Your IDE
===============

Development is better with an IDE. For python, most of our team uses VSCode. Here's how to install
VSCode and set it up to work well with TCode.

Prerequisites
-------------
We're assuming that you're coming from the previous tutorial and are assuming the following:
  - You have a compatible python version installed (3.11+)
  - You have ``uv`` installed and available on your command line
  - You have a ``uv`` environment with ``tcode-api`` installed

If any of this looks unfamiliar, back you go to the previous tutorial.

.. note::
   We recommend using a virtual environment manager like ``uv`` to manage your python.
   If you prefer to use ``venv`` or ``conda``, you can still follow along, but some
   commands will be different.

Install VSCode
--------------

Follow the instructions on their website for your computer's operating system:

https://code.visualstudio.com/download

Open Project in VSCode
----------------------

In your VSCode window's top menu bar, select "File" > "Open...", then select your project folder.

If you see the pop-up window below, select "Save" and save the workspace as a file. Now, we can
easily re-open our workspace setup.

.. image:: images/save-workspace-popup.png
  :alt: VSCode Save Workspace Popup
  :align: center
  :width: 200px

You should now have an "Explorer" window on the left-hand side of your screen with the files we
saw in the previous tutorial using ``ls``.

.. image:: images/explore-sidebar.png
  :alt: VSCode Save Workspace Popup
  :align: center
  :width: 200px

Select Python Interpreter
-------------------------
Now we need to tell VSCode to use the python environment that we set up using ``uv``.

1. In the VSCode search bar [TODO IMAGE], type the following: ``> Python: Select Interpreter``.

.. image:: images/command-bar.png

2. VSCode will then prompt you with a list of the python versions that you have available.
   If your ``uv`` project is open in VSCode, one of the entries should have a filepath that reads
   ``./.venv/bin/python``. This is the python interpreter that uses the virtual environment (or "venv")
   set up by ``uv``. In my drop-down, it comes "Recommended" (fancy!). Select that one.

.. image:: images/select-interpreter.png

Install VSCode Python Extension
-------------------------------
Finally, in order to get tools to make our Python dev work easier (typehints, docstrings, etc), we
need to install VSCode's handy-dandy python extension.

Navigate to the following link and click the "Install" button, then follow the prompts to open
the installation page in VSCode itself. Clicking "Install" *there* gets you the packages.

https://marketplace.visualstudio.com/items?itemName=ms-python.python

Write Your First Script
-----------------------
Your environment should now be set up! 
