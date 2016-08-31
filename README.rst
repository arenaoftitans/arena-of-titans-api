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


Deploy
======

There are 3 kinds of deployment:

- *prod*: deployment on the production server. The configuration is stored in ``scripts/cli.sh``.
- *staging*: deployment on the staging server so all user can test. The configuration is stored in ``scripts/cli.sh``.
- *testing*: deployment on a user defined server, typically a VM. The configuration is stored in ``scripts/cli-conf.sh``. You can view an example below:

   .. literalinclude:: ../scripts/cli-conf.sh
      :language: bash

In order to deploy the API with uWSGI, the following packages are required:

#. ``jinja2-cli``
#. ``nginx``
#. ``redis``
#. ``sudo``
#. ``uwsgi``
#. ``uwsgi-logger-file``
#. ``uwsgi-plugin-common``
#. ``uwsgi-plugin-python3``
#. ``uwsgi-router-http``

You also need to configure uWSGI emperor in ``/etc/uwsgi.ini``:

.. code:: ini

    [uwsgi]
    pidfile = /run/uwsgi/uwsgi.pid
    emperor = /etc/uwsgi.d
    stats = /run/uwsgi/stats.sock
    emperor-tyrant = true
    plugins = python3
    plugins = logfile


Your ``/etc/sudoers`` file must contain the entry below (remplace *testing* by the type you want to deploy):

.. code::

    # Deploy
    jenselme ALL=(root) NOPASSWD: /usr/bin/chown uwsgi\:uwsgi */testing/api/*/uwsgi.ini
    jenselme ALL=(root) NOPASSWD: /usr/bin/ln -s */testing/api/*/uwsgi.ini /etc/uwsgi.d/aot-api-*.ini
    jenselme ALL=(root) NOPASSWD: /usr/bin/ln -sf /var/run/uwsgi/aot-api-ws-*-*.sock /var/run/uwsgi/aot-api-ws-*-latest.sock
    jenselme ALL=(root) NOPASSWD: /usr/bin/cp redis.conf /etc/redis.d/aot-api*.conf
    jenselme ALL=(root) NOPASSWD: /usr/bin/chown root\:redis /etc/redis.d/*
    jenselme ALL=(root) NOPASSWD: /usr/bin/mkdir -p /var/lib/redis/*
    jenselme ALL=(root) NOPASSWD: /usr/bin/chown -R redis\:redis /var/lib/redis/
    jenselme ALL=(root) NOPASSWD: /usr/bin/systemctl start redis@*
    jenselme ALL=(root) NOPASSWD: /usr/bin/systemctl enable redis@*

    # Collect
    jenselme ALL=(root) NOPASSWD: /usr/bin/rm /etc/uwsgi.d/aot-api*.ini
    jenselme ALL=(root) NOPASSWD: /usr/bin/systemctl disable redis@*
    jenselme ALL=(root) NOPASSWD: /usr/bin/systemctl stop redis@*
    jenselme ALL=(root) NOPASSWD: /usr/bin/rm /etc/redis.d/aot-api-*.conf
    jenselme ALL=(root) NOPASSWD: /usr/bin/rm -rf /var/lib/redis/testing*

You need to create the folder that will contain the configurations for redis instances: ``/etc/redis.d``.

In order for all process to be able to communicate with the right Unix socket, you will need to:

#. Add the ``nginx`` user to the ``uwsgi`` group
#. Add the ``uwsgi`` user to the ``nginx`` group

To set the correct permissions on the log file of the API, you need to add the user that makes the deploy to the ``uwsgi`` group.

