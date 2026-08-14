Testing
=======

The test suite uses `pytest`, `pytest-django`, and PostgreSQL. The repository's
`pyproject.toml` configures Django, enables database reuse by default, and
points pytest at `testing.config.settings`.


Set up the test database
------------------------

From the root of the Daiquiri checkout, install the test dependencies and
create the PostgreSQL test databases:

```bash
uv venv --python 3.13
source .venv/bin/activate
uv pip install -e '.[ci]'
psql -f testing/sql/postgres/setup.sql
```

The SQL script creates the application, data, TAP, and OAI test databases and
loads the data fixtures used by the tests. Run it with a PostgreSQL role that
can create roles and databases.


Run tests
---------

Run the full suite from the repository root:

```bash
pytest
```

Useful variants are:

```bash
pytest --migrations                 # include migration execution
pytest -x                          # stop after the first failure
pytest daiquiri/auth               # test one Daiquiri module
pytest path/to/test_file.py       # test one file
pytest path/to/test_file.py::test_name
```

The default `--reuse-db` setting makes repeated test runs faster. Use
`--create-db` when the test database must be recreated.


Coverage
--------

```bash
pytest --cov=daiquiri
pytest --cov=daiquiri --cov-report=html
```

The HTML report is written to `htmlcov/`.
