SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgrseql',
        'NAME': 'daiquiri_app',
        'USER': 'daiquiri_app',
        'PASSWORD': 'daiquiri_app'
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'TAP_SCHEMA',
        'USER': 'daiquiri_tap',
        'PASSWORD': 'daiquiri_tap'
    },
    'data': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data'
    }
}

ADAPTER_DATABASE = 'daiquiri.core.adapter.database.mysql.MySQLAdapter'
ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.mysqldump.MysqldumpAdapter'

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'daiquiri_app',
#         'USER': 'daiquiri_app',
#         'PASSWORD': 'daiquiri_app',
#         'HOST': '127.0.0.1'
#     },
#     'tap': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'OPTIONS': {
#             'options': '-c search_path=TAP_SCHEMA'
#         },
#         'NAME': 'daiquiri_data',
#         'USER': 'daiquiri_tap',
#         'PASSWORD': 'daiquiri_tap',
#         'HOST': '127.0.0.1'
#     },
#     'data': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'daiquiri_data',
#         'USER': 'daiquiri_data',
#         'PASSWORD': 'daiquiri_data',
#         'HOST': '127.0.0.1',
#         'PORT': 5432
#     }
# }

# ADAPTER_DATABASE = 'daiquiri.core.adapter.database.postgres.PostgreSQLAdapter'
# ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.pgdump.PgDumpAdapter'
