Development
===========

This document describes development of the Daiquiri library. Installation and
deployment of a Daiquiri application are documented in the separate
[Daiquiri documentation](https://django-daiquiri.github.io/docs/installation/).


Set up a development environment
---------------------------------

Daiquiri currently requires Python 3.13 or newer. From the root of a checkout,
create a virtual environment and install the development and PostgreSQL test
dependencies:

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e '.[ci]'
```

The `ci` extra contains the test dependencies and the PostgreSQL driver used by
the test settings. The project also declares all runtime dependencies in
`pyproject.toml`, so a separate query-parser checkout or manual ANTLR build is
not required.


Run the test suite
------------------

The test suite uses PostgreSQL and the settings in `testing/config/settings`.
Create the test roles, databases, and fixture data from the repository root as
a PostgreSQL administrator:

```bash
psql -f testing/sql/postgres/setup.sql
```

The complete test commands are described in [testing.md](testing.md).


Use Daiquiri with `dq-dev`
---------------------------

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
testing asynchronous behavior.
