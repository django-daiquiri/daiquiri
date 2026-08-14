Contributing to Daiquiri
========================

Thank you for your interest in improving Daiquiri. This guide describes the
usual workflow for proposing changes to the library.


Before you start
----------------

Before starting substantial work:

* Search the existing issues and pull requests for related work.
* Comment on an existing issue when your work is related to it.
* Open a new issue when you have found a bug or want to propose a feature.
* For larger changes, discuss the approach with the maintainers before
  investing significant implementation effort.

Small fixes, documentation updates, and test improvements can usually be
submitted directly as pull requests.


Create a development branch
---------------------------

Work in a fork of the repository and keep the official repository as an
`upstream` remote:

.. code-block:: console

   git clone git@github.com:YOUR_GITHUB_USER/daiquiri.git
   cd daiquiri
   git remote add upstream https://github.com/django-daiquiri/daiquiri.git
   git fetch upstream

Create a focused branch from ``dev``. Use a short, descriptive name such as
``fix-login-form`` or ``add-cone-search-test``:

.. code-block:: console

   git switch --create fix-login-form upstream/dev

Keep unrelated changes out of the branch. Pull requests should target
``dev`` unless a maintainer asks for a different target branch.


Preferred development workflow: ``dq-dev``
------------------------------------------

Most Daiquiri development is done with ``dq-dev``. It mounts the application
and the Daiquiri source into containers, so changes to the Python source can be
tested immediately in a browser without maintaining the application services
manually.

This workflow requires Docker Engine and Docker Compose v2. Clone the
application and ``dq-dev`` repositories alongside the Daiquiri checkout:

.. code-block:: console

   git clone https://github.com/django-daiquiri/app.git
   git clone https://github.com/django-daiquiri/dq-dev.git

Install ``dq-dev`` with pip and create an active profile:

.. code-block:: console

   cd dq-dev
   python -m pip install .
   python manage.py -c daiquiri-dev
   python manage.py -s daiquiri-dev

Edit ``usr/profiles/daiquiri-dev/conf.toml`` and set the host-side paths to
the application and the Daiquiri source:

.. code-block:: toml

   [folders_on_host]
   dq_app = "/path/to/app"
   dq_source = "/path/to/daiquiri"

The corresponding entries in ``[docker_volume_mountpoints]`` should remain at
their container paths. In ``[env.daiquiri]``, keep the development defaults:

.. code-block:: toml

   debug = true
   enable_gunicorn = false

Start the profile:

.. code-block:: console

   python manage.py -r

The application is available at ``http://localhost:9280``. Edit the Daiquiri
source on the host and refresh the browser to see the result. ``debug=true``
and ``enable_gunicorn=false`` use Django's development server with automatic
reload.


Run local checks
----------------

Install the pre-commit hooks once for the checkout:

.. code-block:: console

   pre-commit install

Before opening or updating a pull request, run the checks that apply to your
change:

.. code-block:: console

   pre-commit run --all-files
   pytest
   pytest --migrations

The project reuses the test database by default. Use ``--create-db`` when the
test database needs to be recreated. The migration-enabled test run is the
closest local equivalent to the database checks performed by continuous
integration.

Full local installation
------------------------

If you prefer to run all services directly on the host instead of using
``dq-dev``, Daiquiri requires Python 3.13 or newer. Create a virtual
environment and install the development, test, and PostgreSQL dependencies:

.. code-block:: console

   python3.13 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -e ".[dev,postgres]"

The repository uses PostgreSQL for its test suite. Follow the `development
guide <docs/development.md>`_ and `testing guide <docs/testing.md>`_ to create
the test databases and load the test data. This manual setup also requires you
to manage the application database, scientific database, web server, and any
asynchronous workers yourself.


Prepare a pull request
----------------------

Keep commits focused and describe the problem and solution clearly in the pull
request. Include the relevant issue when one exists. Before submitting, check
that the pull request:

* includes or updates tests for changed behavior;
* includes migrations, settings, or API documentation when needed;
* updates relevant documentation;
* explains any compatibility, deployment, or data-migration considerations;
* reports the local checks that were run; and
* calls out known limitations or follow-up work.

Update the branch from ``upstream/dev`` before requesting review when it has
fallen behind:

.. code-block:: console

   git fetch upstream
   git rebase upstream/dev
   git push --force-with-lease origin fix-login-form


Maintainer review
-----------------

From an official repository checkout, fetch a pull request's head branch and
check it out in a separate working tree or branch:

.. code-block:: console

   git fetch origin pull/<PR-ID>/head:pr/<PR-ID>
   git switch pr/<PR-ID>

Run the same local checks described above, including the migration-enabled test
run. For changes that affect application behavior, deployment, queues,
database integration, or static assets, also run the relevant ``dq-dev``
integration tests. When a change is specific to a service application, test
that service application as well.

Report failures with the command, environment, and relevant logs so that the
author can reproduce them.
