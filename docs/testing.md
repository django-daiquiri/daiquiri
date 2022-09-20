Testing
=======

Setup tests
-----------

First, create a `local.py` file:


```bash
cp testing/config/settings/sample.local.py testing/config/settings/local.py
```

Afterwards edit the `local.py` as for a regular Daiquiri instance.

The, setup the database:

```bash
# postgres
psql < testing/sql/postgres/test.sql
cat testing/sql/postgres/data/* | psql test_daiquiri_data

# mysql
mysql < testing/sql/mysql/test.sql
cat testing/sql/mysql/data/* | mysql
```

Running tests
-------------

```bash
# from the root directory of the daiquiri repo
pytest --reuse-db                                               
pytest --reuse-db -x                                                       # stop after the first failed test
pytest --reuse-db daiquiri/auth                                            # test only the auth app
pytest --reuse-db daiquiri/auth/tests/test_accounts.py                     # run only a specific test file
pytest --reuse-db daiquiri/auth/tests/test_accounts.py::test_login         # run only a specific test
```


Coverage
--------

```bash
pytest --reuse-db --cov                    # show a coverage report in the terminal
pytest --reuse-db --cov --cov-report html  # additionally create a browsable coverage report in htmlcov/
pytest --reuse-db --cov=daiquiri/auth      # only compute coverage for the auth app
```

Fixtures
--------

The fixtures for testing are created in the following way:

```
./manage.py dumpdata auth.group auth.user account.emailaddress daiquiri_auth.profile > fixtures/auth.json
./manage.py dumpdata daiquiri_contact > fixtures/contact.json
./manage.py dumpdata daiquiri_metadata > fixtures/metadata.json
./manage.py dumpdata daiquiri_jobs.job > fixtures/jobs.json
./manage.py dumpdata daiquiri_query.queryjob > fixtures/queryjobs.json
./manage.py dumpdata daiquiri_query.examples > fixtures/examples.json
```
