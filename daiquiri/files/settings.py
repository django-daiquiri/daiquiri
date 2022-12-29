import daiquiri.core.env as env

FILES_BASE_PATH = env.get_abspath('FILES_BASE_PATH')
FILES_BASE_URL = env.get('FILES_BASE_URL')

FILES_DOCS_PATH = env.get('FILES_DOCS_PATH', 'cms')
