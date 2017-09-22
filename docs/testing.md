Testing
=======

Running tests
-------------

```
testing/runtests.py
testing/runtests.py -k              # keep the database between test runs
testing/runtests.py daiquiri.query  # test only the query app
```

Coverage
--------

```
coverage run testing/runtests.py
coverage report                     # show a coverage report in the terminal
coverage html                       # create browsable coverage report in htmlcov/
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
