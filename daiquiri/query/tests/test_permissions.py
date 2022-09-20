from django.contrib.auth.models import User

from daiquiri.query.process import check_permissions


def test_columns(db):
    user = User.objects.get(username='admin')
    keywords = []
    tables = [('daiquiri_data_obs', 'stars')]
    columns = [
        ('daiquiri_data_obs', 'stars', 'ra'),
        ('daiquiri_data_obs', 'stars', 'dec')
    ]
    functions = []

    result = check_permissions(user, keywords, tables, columns, functions)

    assert result == []


def test_columns_not_found(db):
    user = User.objects.get(username='admin')
    keywords = []
    tables = [('daiquiri_data_obs', 'stars')]
    columns = [
        ('daiquiri_data_obs', 'stars', 'ra'),
        ('daiquiri_data_obs', 'stars', 'not_found')
    ]
    functions = []

    result = check_permissions(user, keywords, tables, columns, functions)

    assert result == ['Column not_found not found.']


def test_alias(db):
    user = User.objects.get(username='admin')
    keywords = []
    tables = [('daiquiri_data_obs', 'stars')]
    columns = [
        ('daiquiri_data_obs', 'stars', 'ra'),
        ('daiquiri_data_obs', 'stars', 'dec'),
        (None, None, 'alias')
    ]
    functions = []

    result = check_permissions(user, keywords, tables, columns, functions)

    assert result == []


def test_missing_schema(db):
    user = User.objects.get(username='admin')
    keywords = []
    tables = [(None, 'stars')]
    columns = [
        ('daiquiri_data_obs', 'stars', 'ra'),
        ('daiquiri_data_obs', 'stars', 'dec'),
        (None, None, 'alias')
    ]
    functions = []

    result = check_permissions(user, keywords, tables, columns, functions)

    assert result == ['No schema given for table stars.']


def test_missing_table(db):
    user = User.objects.get(username='admin')
    keywords = []
    tables = [('daiquiri_data_obs', None)]
    columns = [
        ('daiquiri_data_obs', 'stars', 'ra'),
        ('daiquiri_data_obs', 'stars', 'dec'),
        (None, None, 'alias')
    ]
    functions = []

    result = check_permissions(user, keywords, tables, columns, functions)

    assert result == ['No table given for schema daiquiri_data_obs.']


def test_user_schema(db):
    user = User.objects.get(username='user')
    keywords = []
    tables = [('daiquiri_user_user', 'test')]
    columns = [
        (None, None, '*')
    ]
    functions = []

    result = check_permissions(user, keywords, tables, columns, functions)

    assert result == []
