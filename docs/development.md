Development setup
-----------------

Install `npm`:

```
sudo apt-get install npm
```

Install `bower`:

```
sudo npm -g install bower
```

Create a `django-daiquiri` directory at a convenient place:

```
mkdir django-daiquiri
cd django-daiquiri
mkdir log
```

Set up a virtualenv in this directory:

```
virtualenv env
source env/bin/activate
```

Clone the repositories and call the `daiquiri` and `app`:

```
git clone https://github.com/aipescience/django-daiquiri daiquiri
git clone https://github.com/aipescience/django-daiquiri-app app
```

Install the requirements:

```
cd app
pip install -r requirements/base.txt
pip install -r requirements/mysql.txt
```

Copy the `local.py` settings file:

```
cp daiquiri_app/settings/sample.local.py daiquiri_app/settings/local.py
```

Edit daiquiri_app/settings/local.py for database settings and 'DEBUG = True' and add

```
import sys; sys.path.append('../daiquiri/')
```

at the top of the file.

Run:

```
./manage.py migrate
./manage.py bower install
./manage.py createsuperuser
```

Run the development server:

```
./manage.py runserver
```

Go to `http://localhost:8000` in your web browser.

### Additional settings 

### Antlr
You have to have Antlr installed. Please check [Antlr website](wwww. antlr.org) for the newest version of the installation script! 

```
cd /usr/local/lib
wget http://www.antlr.org/download/antlr-4.5.3-complete.jar
export CLASSPATH=".:/usr/local/lib/antlr-4.5.3-complete.jar:$CLASSPATH"
alias antlr4='java -jar /usr/local/lib/antlr-4.5.3-complete.jar'
alias grun='java org.antlr.v4.gui.TestRig'
```

### Queryparser
As long as pip install is in development, install the [Queryparser](https://github.com/aipescience/queryparser). 


#### MariaDB

The default character set in MariaDB 10.0.27 is utf8b4. This causes a django-error for the migration:

```
django.db.utils.OperationalError: (1071, 'Specified key was too long; max key length is 767 bytes')
```
Solution 1: set the django DB settings: [https://docs.djangoproject.com/el/1.10/ref/settings/#charset]


Solution 2: create your database with the utf8 character set.
```
create database <DBname> CHARACTER SET utf8;
```

#### Ubuntu 16.04
Errror:
```
./manage.py bower install
Problem:/usr/bin/env: ‘node’: No such file or directory
```
Solution:
```
sudo apt-get install nodejs-legacy
```