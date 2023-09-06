========
salt-sls
========

.. image:: https://img.shields.io/badge/made%20with-pop-teal
   :alt: Made with pop, a Python implementation of Plugin Oriented Programming
   :target: https://pop.readthedocs.io/

.. image:: https://img.shields.io/badge/made%20with-python-yellow
   :alt: Made with Python
   :target: https://www.python.org/


Run a single SLS file locally with Salt, without the need for a master or minion setup. This agentless and simplified approach allows faster deployment and testing of SLS files.


About
=====

`salt-sls` is an innovation for those who want a lightweight approach to using SaltStack. With this tool, you can run a single SLS file on your local machine without setting up the more extensive master or minion infrastructure. Whether you're testing a new SLS or need a quick execution, `salt-sls` is your friend.


What is POP?
------------

This project is built with `pop <https://pop.readthedocs.io/>`__, a Python-based
implementation of *Plugin Oriented Programming (POP)*. POP seeks to bring
together concepts and wisdom from the history of computing in new ways to solve
modern computing problems.

For more information:

* `Intro to Plugin Oriented Programming (POP) <https://pop-book.readthedocs.io/en/latest/>`__
* `pop-awesome <https://gitlab.com/vmware/pop/pop-awesome>`__
* `pop-create <https://gitlab.com/vmware/pop/pop-create/>`__

Getting Started
===============

Prerequisites
-------------

* Python 3.8+
* git *(if installing from source, or contributing to the project)*

Installation
------------

If wanting to use ``salt-sls``, you can do so by either
installing from PyPI or from source.

Install from PyPI
+++++++++++++++++

   .. code-block:: bash

      pip install salt-sls

Install from source
+++++++++++++++++++

.. code-block:: bash

   # clone repo
   git clone git@vmware/pop/salt-sls.git
   cd salt-sls

   # Setup venv
   python3 -m venv .venv
   source .venv/bin/activate
   pip install .

Usage
=====

Examples
--------

To run your SLS files, you can use either the standard Python command or the convenient `sls` command.
You can also set specific configuration options through a `my_config.yaml` file.


Using the standard Python command in the cloned repo:

.. code-block:: bash

   python run.py examples/test.sls

Or using the `sls` command from pypi:

.. code-block:: bash

   echo "test:\n  test.nop:\n    - name: state" > test.sls
   sls test.sls

Configuration
=============

Set up configuration options for `salt-sls` through a `my_config.yaml` file. Here's an example:

.. code-block:: yaml

   # my_config.yaml
   salt_sls:
     cachedir: /var/log/salt
     # Add any minion config opts you want to use under the "minion_opts" key.
     # Refer to the [official minion config documentation](https://docs.saltproject.io/en/latest/ref/configuration/minion.html) for details.
     minion_opts: {}

Roadmap
=======

Reference the `open issues <https://gitlab.com/vmware/pop/salt-sls/issues>`__ for a list of
proposed features (and known issues).

Acknowledgements
================

* `Img Shields <https://shields.io>`__ for making repository badges easy.
