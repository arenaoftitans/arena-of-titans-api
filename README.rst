Arena of Titans – API
=====================

This README gives the most important things you need to know in order to develop
or use the Arena of Titans API.

.. contents::


Requirements
============

#. `Python <https://www.python.org/>`__ 3.6 or above.
#. Recent version of `docker <https://www.docker.com/>`__ and `docker-compose <https://docs.docker.com/compose/install/>`__. Versions that are known work: ``Docker version 1.13.1, build 27e468e/1.13.1``, ``docker-compose version 1.14.0, build c7bdf9e``.
#. `git <https://www.git-scm.com>`__ 2.0 or above.

Using with docker
-----------------

**Note:** If you intend to use the API with docker and docker-compose, this is the only relevant section.

Run ``docker-compose up`` to run the API. You can check it is fine by opening http://localhost:8181 in a browser. You should see the default autobahn page.

You can also use ``make dev`` to start docker compose.

Each time you edit a file, the API will be reloaded automatically to ease development.


Installing Python dependencies
------------------------------

Windows users, read the section about Windows below.

#. Create a venv: ``python3 -m venv .venv``
#. Enable the virtualenv `` source .venv/bin/activate``
#. Install these libraries so you can build the dependencies:

   - libxml2-devel
   - libxslt-devel

   On debian based system, use this list:

   - libxml2-dev
   - libxslt-dev

#. Install the dependencies: ``pip install -r requires.txt``
#. Install the tests dependencies: ``pip install -r tests_requires.txt``

On Windows
++++++++++

#. Before creating the venv you will need to open a PowerShell terminal as root and run:

   .. code::

      cd ..
      Set-ExecutionPolicy Unrestricted

#. Create the venv: ``python3 -m venv .venv`` If the creation fails due to ``python3 not found``, check that:

   - python3 was added to your your PATH during install.
   - Make a copy of your ``python.exe`` executable into ``python3.exe``

#. Enable the venv: ``.venv\Scripts\activate``
#. Install the dependencies: ``pip install -r requires.txt``
#. Install the tests dependencies: ``pip install -r tests_requires.txt``

Creating the development configuration
--------------------------------------

Copy ``config/config.staging.toml`` into ``config/config.dev.toml``. Then adapt the values. There are two cases for this:

- You want the API to be directly accessible with TCP (**this is the only supported case on Windows**): comment the lines ``api.socket`` (or put an empty value). If you already use the port 9000 for another application, change ``api.ws_port`` to something free on your system.
- You want the API to be behind nginx like in production/staging:

  - Correct ``api.server_name`` to match the host you will use.
  - Correct the path of the socket to something like ``api.socket = '/home/jenselme/projects/aot-api/aot-api-ws-dev-{version}.sock'``

In both cases, you should comment ``cache.socket`` or put an empty value in it to connect with TCP to redis.

You should now be ready to launch the unit tests.

#. If you are launching the tests for the first time, launch ``python3 setup.py develop``
#. Launch the tests: ``python3 setup.py test``

Setup redis
-----------

On linux, install the package named ``redis`` and start it with ``systemctl start redis``.
On Windows, download the last release from `MS Open Tech <https://github.com/MSOpenTech/redis/releases>`__ and install it.

#. Please copy the configuration distributed with the API (``config.dist.toml``)
   into ``config.toml`` and modify its entry to match your needs.
#. The API needs `redis <http://redis.io/>`_ to store its information. It must
   be installed and running for the API to work.
#. The API is design to run behind a nginx server. A sample nginx configuration
   file is provided with the API: ``aot-api.dist.conf``.


Usage
=====

Use the ``make`` command to launch task. Tasks will be launched from the host within the docker container by default. Use ``make venvlint`` to run the linter from within a venv instead. Use ``make`` to view the list of possible targets and their description. Alternatively, you can use:

- To launch the API in development mode (reload on modification): ``python3 aot/test_main.py``
- To launch the unit tests with code coverage: ``python3 setup.py test``
- To relaunch the unit tests on each modifications:

   - On Linux: ``ptw aot --runner py.test -- aot/test --testmon``
   - On Windows: ``ptw aot --runner py.test -- aot/test``

.. note::

    You can override any variables in the Makefile by creating a ``Makefile.in`` and specifying the values there like that: ``FLAKE8_CMD = ~/.virtualenvs/aot/bin/flake8``


Contributing
============

Be sure that (this can be configured in your text editor or your IDE):

- Your files are encoded in UTF-8
- You use Unix style line ending (also called LF)
- You remove the trailing whitespaces
- You pull your code using ``git pull --rebase=preserve``

Code style
----------

- Wrap your code in 100 characters to ease reading.
- Use spaces, not tabs.

git hooks
---------

git hooks allow you to launch a script before or after a git command. They are very handy to automatically perform checks. If the script exits with a non 0 status, the git command will be aborted. You must write them in the `.git/hooks/` folder in a file following the convention: ``<pre|post>-<git-action>``. You must not forget to make them executable, eg: ``chmod +x .git/hooks/pre-commit``.

In the case you don't want to launch the hooks, append the ``--no-verify`` option to the git command you want to use.

pre-commit
++++++++++

.. code:: bash

   #!/usr/bin/env bash

   set -e

   flake8 --max-line-length 99 --exclude "conf.py" --exclude "aot/test" --ignore none aot
   flake8 --max-line-length 99 --ignore=F811,F401 aot/test/

pre-push
++++++++

This is only useful if you don't use ``npm run tdd`` during development.

.. code:: bash

   #!/usr/bin/env bash

   set -e

   python3 setup.py test

Commit
------

We try to follow the same `rules as the angular project <https://github.com/angular/angular.js/blob/master/CONTRIBUTING.md#commit>`__ towards commits. Each commit is constituted from a summary line, a body and eventually a footer. Each part are separated with a blank line.

The summary line is as follow: ``<type>(<scope>): <short description>``. It must not end with a dot and must be written in present imperative. Don't capitalize the fist letter. The whole line shouldn't be longer than 80 characters and if possible be between 70 and 75 characters. This is intended to have better logs.

The possible types are :

- chore for changes in the build process or auxiliary tools.
- doc for documentation
- feat for new features
- ref: for refactoring
- style for modifications that not change the meaning of the code.
- test: for tests

The body should be written in imperative. It can contain multiple paragraph. Feel free to use bullet points.

Use the footer to reference issue, pull requests or other commits.

This is a full example:

::

   feat(css): use CSS sprites to speed page loading

   - Generate sprites with the gulp-sprite-generator plugin.
   - Add a build-sprites task in gulpfile

   Close #24
