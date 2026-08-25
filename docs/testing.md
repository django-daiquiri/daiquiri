Testing
=======

The test suite uses `pytest`, `pytest-django`, and PostgreSQL. The repository's
`pyproject.toml` configures Django, enables database reuse by default, and
points pytest at `testing.config.settings`.

Continuous integration runs the complete suite for pushes and pull requests.
Running it manually is optional and is mainly useful when reproducing a CI
failure. The default `dq-dev` container uses an application's runtime
configuration and databases, so it is not a drop-in environment for these
tests.


Set up the test database
------------------------

From the root of the Daiquiri checkout, install Python 3.13 or newer, install
the test dependencies, and create the PostgreSQL test databases:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[ci]'
psql -f testing/sql/postgres/setup.sql
```

The SQL script creates the application, data, TAP, and OAI test databases and
loads the data fixtures used by the tests. Run it with a PostgreSQL role that
can create roles and databases.


Run tests
---------

Run the full suite from the repository root:

```bash
python -m pytest
```

Useful variants are:

```bash
python -m pytest --migrations                 # include migration execution
python -m pytest -x                          # stop after the first failure
python -m pytest daiquiri/auth               # test one Daiquiri module
python -m pytest path/to/test_file.py        # test one file
python -m pytest path/to/test_file.py::test_name
```

The default `--reuse-db` setting makes repeated test runs faster. Use
`--create-db` when the test database must be recreated.


Coverage
--------

```bash
python -m pytest --cov=daiquiri
python -m pytest --cov=daiquiri --cov-report=html
```

The HTML report is written to `htmlcov/`.
