Daiquiri (Django version)
=========================

**A framework for the publication of scientific databases**

[![pytest Workflow Status](https://github.com/django-daiquiri/daiquiri/actions/workflows/pytest.yml/badge.svg)](https://github.com/django-daiquiri/daiquiri/actions/workflows/pytest.yml)
[![Coverage Status](https://coveralls.io/repos/django-daiquiri/daiquiri/badge.svg?branch=master&service=github)](https://coveralls.io/github/django-daiquiri/daiquiri?branch=master)
[![License](http://img.shields.io/badge/license-APACHE-blue.svg?style=flat)](https://github.com/django-daiquiri/daiquiri/blob/master/LICENSE)
[![Latest Version](https://img.shields.io/pypi/v/django-daiquiri.svg?style=flat)](https://pypi.org/project/django-daiquiri/)

This project is still in development. [gaia.aip.de](https://gaia.aip.de) is based on this version of Daiquiri.

The legacy version of Daiquiri written in PHP can be found [here](https://github.com/aipescience/daiquiri).


Quick start
-----------

### Install prerequisites

```bash
apt-get install -y git build-essential libxml2-dev libxslt-dev zlib1g-dev libssl-dev
apt-get install -y mariadb-client mariadb-server libmariadb-dev libmariadbclient-dev libmariadb-dev-compat
```

More about Daiquiri's prerequisites including different Linux distributions can be found [here](https://github.com/aipescience/django-daiquiri/tree/master/docs/prerequisites.md).

### Fork the daiquiri-app

```bash
git clone https://github.com/django-daiquiri/app app
```

### Set up the virtual enviroment and install dependencies

```bash
cd app
python3 -m venv env
source env/bin/activate
pip install django-daiquiri mysqlclient
```

### Setup Daiquiri

```bash
cp config/settings/sample.local.py config/settings/local.py
mkdir log download

./manage.py sqlcreate               # shows the commands to be executed on the database
./manage.py migrate                 # creates database and tables
./manage.py migrate --database=tap  # creates TAP_SCHEMA
./manage.py createsuperuser         # creates admin user
./manage.py runserver               # runs a development server
```

Navigate to http://localhost:8000 in your browser.

Documentation
-------------

* **Main documenation**:  [django-daiquiri.github.io](https://django-daiquiri.github.io)

