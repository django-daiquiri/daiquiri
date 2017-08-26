Testing
=======

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
