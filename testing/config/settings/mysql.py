SECRET_KEY = 'this is a not very secret key'

# all test databases need to have different name or they will not be picked up by django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'daiquiri_app',
        'USER': 'daiquiri_app',
        'PASSWORD': 'daiquiri_app',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_app',
        },
    },
    'data': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_data',
        },
    },
    'tap': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tap_schema',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_tap_schema',
        },
    },
    'oai': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'oai_schema',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_oai_schema',
        },
    },
}

ADAPTER_DATABASE = 'daiquiri.core.adapter.database.mysql.MySQLAdapter'
ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.mysqldump.MysqldumpAdapter'
