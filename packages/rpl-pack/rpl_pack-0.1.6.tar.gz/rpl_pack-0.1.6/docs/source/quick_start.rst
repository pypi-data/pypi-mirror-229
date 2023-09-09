Quick Start
===========

.. _registeration:

Registration
------------

Using rpl-pack requires an active RPL account at the `RPL Website <https://rock-physics-lab.herokuapp.com>`_.
Once you've created an account, you can then follow the installation guide below.

.. _installation:

Installation
------------

It's a good idea to keep everything contained in a virtual environment, which can be
created either with Python's `venv module <https://docs.python.org/3/library/venv.html>`_ or
with `Conda <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands>`_.


.. tabs::

    .. group-tab:: venv

        .. code-block:: console

            $ python3 -m venv .venv
    
    .. group-tab:: conda

        .. code-block:: console

            $ conda create --name .venv 


Install rpl-pack with pip.

.. tabs::

    .. group-tab:: pip

        .. code-block:: console

            (.venv) $ pip install rpl-pack

Great! If everything went accordingly then we can move on to the :doc:`tutorials` section to
learn more about the API, what is included, and how to leverage it in your own scripts. In case
something went wrong, please head over to the :doc:`faq` section or :doc:`contact_us`.
