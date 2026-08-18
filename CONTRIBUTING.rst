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

Run the pre-commit checks before every commit. They are the primary local
checks for day-to-day development. Install them once in the Python environment
used for development:

.. code-block:: console

   python -m pip install pre-commit
   pre-commit install

Run all configured hooks explicitly before opening or updating a pull request:

.. code-block:: console

   pre-commit run --all-files

Some hooks can modify files. Review those changes and run the command again
until it completes successfully.

Continuous integration runs the complete PostgreSQL-backed pytest suite for
pushes and pull requests. The default ``dq-dev`` container is an application
development environment, not the test environment used by this suite, so
running ``pytest`` there is not part of the normal development workflow.


Optional: run CI locally with ``act``
-------------------------------------

If you want to run the CI workflow locally, install `act
<https://github.com/nektos/act>`_ and make sure Docker Engine is running. From
the Daiquiri repository root, run:

.. code-block:: console

   act workflow_dispatch \
      -W .github/workflows/pytest.yml \
      -j build \
      --input use_current_workspace=true \
      --bind

This runs the PostgreSQL-backed workflow against the current working tree.
Manual workflow runs do not publish coverage by default. The GitHub Actions
result remains authoritative because ``act`` uses a local runner that is not
identical to GitHub-hosted Actions.

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

Run ``pre-commit run --all-files`` and rely on CI for the complete pytest suite.
Use ``act`` when reproducing the CI environment locally is useful. For changes
that affect application behavior, deployment, queues, database integration, or
static assets, also run the relevant ``dq-dev`` integration tests. When a
change is specific to a service application, test that service application as
well.

Report failures with the command, environment, and relevant logs so that the
author can reproduce them.


Release process
---------------

For a standard release:

1. On ``dev``, update the version in ``daiquiri/__init__.py`` and
   ``package.json``. With npm installed, synchronize ``package-lock.json``:

   .. code-block:: console

      npm install --package-lock-only

   Commit and push all three version files on ``dev``.
2. Wait for CI and merge the release pull request into ``main``.
3. Update the local ``main`` checkout:

   .. code-block:: console

      git switch main
      git pull --ff-only origin main

4. Make sure the active ``dq-dev`` profile points ``dq_source`` to the
   Daiquiri checkout, then build and check the package:

   .. code-block:: console

      cd /path/to/dq-dev
      python manage.py --build-release

   This creates and checks the files in the Daiquiri ``dist/`` directory. It
   does not upload them.
5. Upload the checked package manually:

   .. code-block:: console

      cd /path/to/daiquiri
      twine upload dist/*

6. Test the exact PyPI version with ``dq_source`` disabled in ``dq-dev``.
   Confirm the application installs Daiquiri from PyPI and works as expected.
7. Tag the merged ``main`` branch and push the tag:

   .. code-block:: console

      git switch main
      git pull --ff-only origin main
      git tag 1.3.9
      git push origin 1.3.9

8. Create the GitHub release for the tag and clean up the generated release
   notes.

For optional ``.dev`` releases, PyPI testing, configuration details, and
troubleshooting, see the `detailed release guide
<https://django-daiquiri.github.io/docs/release/>`_.
