Arena of Titans – API
=====================

This README gives the most important things you need to know in order to develop
or use the Arena of Titans API.

.. contents::


Requirements
============

#. The project is written in python 3 and requires Python 3.4 or above.
#. Make
#. The list of python dependencies are listed in ``requires.txt``. You can
   install them with pip: ``pip install -r requires.txt``.
#. The dependencies required to launch tests are listed in
   ``tests_require.txt``. You can install them with pip: ``pip install -r
   tests_require.txt``.
#. Please copy the configuration distributed with the API (``config.dist.toml``)
   into ``config.toml`` and modify its entry to match your needs.
#. The API needs `redis <http://redis.io/>`_ to store its information. It must
   be installed and running for the API to work. In order to launch the
   integration tests, you also need it to be running.
#. The API is design to run behind a nginx server. A sample nginx configuration
   file is provided with the API: ``aot-api.dist.conf``.

You may want to install:

#. `jinja2-cli <https://pypi.python.org/pypi/jinja2-cli>`_ (``pip install
   jinja2-cli2``) which is needed to generate the nginx configuration file from
   the template (``aot-api.dist.conf``) and the configuration file
   ``config.toml``. You can use ``make config`` to do this.
#. `forever <https://github.com/foreverjs/forever>`_ (**this is a nodejs
   program**, install it with ``npm install -g forever``). This program is used
   to automatically restart the API if a file changes and to automatically
   restart it on production if it crashes. ``forever`` is used by the following
   make targets: ``testintegration``, ``start``, ``debug``.


Usage
=====

Use the ``make`` command to launch task. Use ``make help`` to view the list of
possible targets and their description.
