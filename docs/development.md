Development setup
=================

Install prerequisites
---------------------

Install the prerequisites for your Linux distribution as described [here](prerequisites).


Create user
-----------

Either run Daiquiri as your regular Desktop user or create a dedicated user:

```
useradd -m -d /srv/daiquiri daiquiri -s /bin/bash
su - daiquiri
```

Don't run Daiquiri as root!


Obtain repositories
-------------------

Clone the repositories and call them `daiquiri`, `app`, and `queryparser`:

```
git clone https://github.com/django-daiquiri/daiquiri daiquiri
git clone https://github.com/django-daiquiri/app app
git clone https://github.com/django-daiquiri/queryparser queryparser
```

Build the queryparser
---------------------

Change to the queryparser directory, fetch `antlr` and run `make`:

```
cd queryparser
wget http://www.antlr.org/download/antlr-4.7.2-complete.jar
make
```

Install python dependencies
---------------------------

Change to the `app` directory and create a virtualenv:

```
cd ../app
virtualenv env
source env/bin/activate
```

or for `python3`:

```
cd ../app
python3 -m venv env3
source env3/bin/activate
```

Install the requirements in editable mode:

```
pip install -e ../daiquiri
pip install -e ../queryparser
pip install mysqlclient
pip install psycopg2-binary
```
or for postgres:
```
pip install psycopg2
```

Setup the app
-------------

Create a `log` and a `download` directory:

```
mkdir log download
```

Copy the `local.py` settings file:

```
cp config/settings/sample.local.py config/settings/local.py
```

Edit config/settings/local.py for database settings, and `DEBUG = True` and add

```
TESTING_DIR = os.path.join(BASE_DIR, '../daiquiri/testing')

FIXTURE_DIRS = (
    os.path.join(TESTING_DIR, 'fixtures'),
)

AUTH_SIGNUP = True
AUTH_WORKFLOW = 'confirmation'

ARCHIVE_ANONYMOUS = False
ARCHIVE_BASE_PATH = os.path.join(TESTING_DIR, 'files')

FILES_BASE_PATH = os.path.join(TESTING_DIR, 'files')

SERVE_DOWNLOAD_DIR = os.path.join(TESTING_DIR, 'files')
```

at the end of the file.

Next, the differenet users and permissions need to be created on the database. For this purpose, the `sqlcreate` can be used to see what needs to be executed on the database:

```
./manage.py sqlcreate                             # databases, users and permissions to run daiquiri
./manage.py sqlcreate --test                      # databases, users and permissions to run tests
./manage.py sqlcreate --schema=daiquiri_data_obs  # databases, users and permissions to use a particular schema with scientific data
```

Copy the output line by line to a database shell, and create the test databases using the files in `../daiquiri/testing/sql`, for MySQL:

```
mysql < ../daiquiri/testing/sql/mysql.sql
```

and for PostgreSQL:

```
psql daiquiri_data < ../daiquiri/testing/sql/postgres.sql
psql daiquiri_data < ../daiquiri/testing/sql/postgres_permissions.sql
psql test_daiquiri_data < ../daiquiri/testing/sql/postgres.sql
psql test_daiquiri_data < ../daiquiri/testing/sql/postgres_permissions.sql
```

Create the front end library vendor bundles:

```
./manage.py download_vendor_files
```

Run the tests:

```
./manage.py test daiquiri --keepdb
```

Run the database migrations:

```
./manage.py migrate
./manage.py migrate --database=data
```

Import the fixtures:

```
./manage.py loaddata ../daiquiri/testing/fixtures/*
```

Run the development server:

```
./manage.py runserver
```

Go to `http://localhost:8000` in your web browser.


Setup the queues
----------------

Edit config/settings/local.py again, and set `ASYNC = True`.


Open three other terminals, go to the `app` directory, activate the virtual environment, and run:

```
./manage.py runworker
```

```
./manage.py runworker query
```

```
./manage.py runworker download
```

to start the different workers.


Additioal information
---------------------

MariaDB
~~~~~~~

The default character set in MariaDB 10.0.27 is utf8b4. This causes a django-error for the migration:

```
django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 767 bytes')
```

Solution 1: set the django DB settings: [https://docs.djangoproject.com/el/1.10/ref/settings/#charset]

Solution 2: create your database with the utf8 character set.

```
create database <DBname> CHARACTER SET utf8;
```
