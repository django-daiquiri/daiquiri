Installation
============

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


Clone the app
-------------

Clone the [django-daiquiri-app](https://github.com/aipescience/django-daiquiri-app) to a directory of your choice:

```
git clone https://github.com/aipescience/django-daiquiri-app app
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
cd app
python3 -m venv env3
source env3/bin/activate
```

Install the requirements in editable mode:

```
pip install -r requirements.txt
pip install mysqlclient
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

Edit config/settings/local.py for database settings, `ASYNC = True`, `DEBUG = True`, and `VENDOR_CDN`.

Create the front end library vendor bundles:

```
./manage.py download_vendor_files
```

Next, the differenet users and permissions need to be created on `mysql`. For this purpose, the `sqlcreate` can be used to see what needs to be executed on the MySQL/MariaDB database:

```
./manage.py sqlcreate
```

Alternatively, for postgres:

```
./manage.py sqlcreate_postgres
```


Either copy the output line by line to a mysql shell, or use a pipe:

```
./manage.py sqlcreate | mysql
```

Run the tests:

```
./manage.py test daiquiri --keepdb
```

Run the database migrations:

```
./manage.py migrate
./manage.py migrate --database=tap
```

Create a superuser

```
./manage.py createsuperuser
```

Run the development server:

```
./manage.py runserver
```

Go to `http://localhost:8000` in your web browser.


Open three other terminals, got to the `app` directory, activate the virtual environment, and run:

```
./manage.py runworker default
```

```
./manage.py runworker query
```

```
./manage.py runworker download
```

to start the different workers.
