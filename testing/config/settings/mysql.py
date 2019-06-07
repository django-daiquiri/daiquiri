SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'daiquiri_app',
        'USER': 'daiquiri_app',
        'PASSWORD': 'daiquiri_app',
        'HOST': '127.0.0.1'
    },
    'data': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_data'
        }
    },
    'tap': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TAP_SCHEMA',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1'
    },
    'oai': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'OAI',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1'
    },
}

ADAPTER_DATABASE = 'daiquiri.core.adapter.database.mysql.MySQLAdapter'
ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.mysqldump.MysqldumpAdapter'
