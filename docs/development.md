Development
===========

This document describes development of the Daiquiri library. Installation and
deployment of a Daiquiri application are documented in the separate
[Daiquiri documentation](https://django-daiquiri.github.io/docs/installation/).


Preferred development workflow: `dq-dev`
----------------------------------------

`dq-dev` is the container-based integration workflow. It can install the
published Daiquiri package, or a local Daiquiri checkout when `dq_source` is
mounted.

This workflow requires Docker Engine and Docker Compose v2. Current Docker
Desktop installations commonly include Compose; on other systems, install the
Docker Compose plugin so that the `docker compose` command is available.

From the `dq-dev` checkout:

```bash
python manage.py -c dev
python manage.py -s dev
```

Edit `usr/profiles/dev/conf.toml` and set the host-side paths for the app and,
when testing local library changes, the Daiquiri source:

```toml
[folders_on_host]
dq_app = "/path/to/app"
dq_source = "/path/to/daiquiri"
```

Leave the corresponding container mount points unchanged. Start the profile
with:

```bash
python manage.py -r
```

The default profile exposes the application at
`http://localhost:9280`. The default configuration runs without asynchronous
workers; enable the required containers and settings in the profile before
testing asynchronous behavior. For live Daiquiri development, keep
`debug = true` and `enable_gunicorn = false` in the Daiquiri environment.


Run pre-commit checks
---------------------

Run the pre-commit checks before every commit. Install the tool once in the
Python environment used for development:

```bash
python -m pip install pre-commit
pre-commit install
```

Run all configured hooks explicitly with:

```bash
pre-commit run --all-files
```

Some hooks can modify files. Review those changes and run the command again
until it completes successfully.


Full test suite
---------------

Continuous integration runs the complete PostgreSQL-backed pytest suite for
pushes and pull requests. The default `dq-dev` container is not configured with
the test settings and databases used by this suite.

If you want to reproduce CI locally, use `act` with the workflow command in
[`CONTRIBUTING.rst`](../CONTRIBUTING.rst). The full manual PostgreSQL setup is
described in [testing.md](testing.md).


Full local installation
-----------------------

If you prefer to run the library and its dependencies directly on the host,
Daiquiri requires Python 3.13 or newer. From the root of a checkout, create a
virtual environment and install the development and PostgreSQL dependencies:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev,postgres]'
```

The project declares all runtime dependencies in `pyproject.toml`, so a
separate query-parser checkout or manual ANTLR build is not required.
