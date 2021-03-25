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

#. Install `pipenv <https://github.com/kennethreitz/pipenv>`__: ``pip install --user pipenv`` (*Note:* make sure ``pip`` relies on Python 3. You may need to use ``pip3`` instead).
#. Create the virtualenv and install all dependencies to run and develop the project: ``pipenv install --dev``
#. Enable the virtualenv: ``pipenv shell``

On Windows
++++++++++

Before creating the venv you will need to open a PowerShell terminal as root and run:

   .. code::

      cd ..
      Set-ExecutionPolicy Unrestricted


Creating the development configuration
--------------------------------------

The configuration is managed in ``aot/config.py``. It contains defaults made for development purposes. You can override any configuration value in a ``.env`` file located at the root of the project or by using environment values. A ``.env`` file can look like:

.. code::

    VERSION=a_test

To find the name of the variable to use, look into ``aot/config.py`` and use the first argument to ``environ.get``. So for ``environ.get('VERSION', 'latest')``, you must use ``VERSION``. The second argument represents the default value.

Setup redis
-----------

On linux, install the package named ``redis`` and start it with ``systemctl start redis``.
On Windows, download the last release from `MS Open Tech <https://github.com/MSOpenTech/redis/releases>`__ and install it.

#. Please copy the configuration distributed with the API (``config.dist.toml``)
   into ``config.toml`` and modify its entry to match your needs.
#. The API needs `redis <http://redis.io/>`_ to store its information. It must
   be installed and running for the API to work. You can also user docker and docker-compose.


Usage
=====

Use the ``make`` command to launch task. Tasks will be launched in the local venv. See the ``DK_EXEC_CMD`` variable and the ``dkcheck`` target to view how to launch things in the container. Use ``make`` to view the list of possible targets and their description. Alternatively, you can use:

- To launch the API in development mode (reload on modification): ``python3 aot --reload``
- To launch the unit tests with code coverage: ``make tests``
- To relaunch the unit tests on each modifications:

   - On Linux: ``make tdd``
   - On Windows: ``ptw aot --runner py.test -- aot/test``

.. note::

    You can override any variables in the Makefile by creating a ``Makefile.in`` and specifying the values there like that: ``FLAKE8_CMD = ~/.virtualenvs/aot/bin/flake8``


Logging
=======

Logs are sent to ``stderr`` from the container. Look there to see them. We don't send anything to a log file to avoid mounting a volume (in production) and managing a log file. If you want to exploit the result of the log outside ``stderr`` configure docker to do so. See `this page <https://docs.docker.com/engine/admin/logging/overview/>`__ of the docker documentation to learn how to configure the proper logging driver.

*Note:* on linux systems, the logs are also send to ``journald`` by default. Use something like ``journalctl -o short --no-hostname -b --all -u docker -f`` or ``journalctl -o short --no-hostname -b --all -u docker -f CONTAINER_ID=28c9e6a5b6af`` to view the logs from ``journald``. You can also use ``journalctl`` to filter and query the logs. Refer to the man page of ``journalctl`` to learn how to do that.


How to
======

Add a trump or a power
----------------------

#. Add the trump and power class if they don't already exist.
#. Add its definition to the resource file.

Update dependencies
-------------------

#. If required, change the version requirements in the ``Pipfile``.
#. Run ``pipenv update --dev`` to update the lock file for all dependencies.
#. Run ``pipenv sync --dev`` to sync local virtual env (if you use it locally outside docker).
#. Run ``make check`` to be sure everything still works.
#. Run ``make VERSION=ver dockerbuild``. Version must be the two last digit of the year, two digits for the month and one digit for the build number. For instance: ``19.07.1`` for the 1st build of July 2019.
#. Update the image version in ``docker-compose.yml``.
#. Stop all the containers with ``docker-compose down`` and re-create them with ``docker-compose up -d``.
#. Run the tests and lint *in the container* with ``make dkcheck``.
#. Push the new image: ``make VERSION=ver dockerpush``.
#. Commit and push the changes.


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

This project uses `pre-commit <https://pre-commit.com/>`__ to handle git hooks automatically. To install the hooks, run ``pre-commit install`` and ``pre-commit install --hook-type pre-push``.

Commit
------

We try to follow the same `rules as the angular project <https://github.com/angular/angular.js/blob/master/DEVELOPERS.md#-git-commit-guidelines>`__ towards commits. Each commit is constituted from a summary line, a body and eventually a footer. Each part are separated with a blank line.

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


Docker
======

#. Build the docker image: ``make VERSION=15.11.1 dockerbuild``. Don't forget to change the tag. It must be like ``<two last digit from year>.<month>.<build-number>``.
#. Login into docker: ``docker login registry.gitlab.com``.
#. Push the image: ``docker push registry.gitlab.com/arenaoftitans/arena-of-titans-api``
#. Change the version of the image in ``docker-compose.yml``

**Note:** If you want to install a new dependency, you must first run ``pipenv lock`` to update the ``Pipenv.lock`` file in a local virtual env or in the container.


Debugger
========

We rely on `pudb <https://pypi.org/project/pudb/>`__ to get a nice, full featured debugger. To add breakpoints, add ``breakpoint()`` at the relevant places in your code. You must then attach to the container of the API with something like (the actual name may differ on your configuration): ``docker attach aotapi_aot-dev-api_1`` to see the debugger window and interact with it.

Notes:

- To close the debugger window, you must hit ``^C-C`` which will also stop the container.
- We can also use remote debugging as described `here <https://github.com/isaacbernat/docker-pudb>`__. To do so, use ``from pudb.remote import set_trace; set_trace(term_size=(160, 40), host='0.0.0.0', port=6900)`` to create the breakpoint and ``telnet 127.0.0.1 6900`` to attach to the debugger. It is not recommended because you need to know in advance the size of the terminal to use, which is cumbersome.
- VSCode debugging is also not very practical. See https://code.visualstudio.com/docs/python/debugging#_remote-debugging
