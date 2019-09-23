import daiquiri.core.env as env

WORDPRESS_PATH = env.get_abspath('WORDPRESS_PATH')
WORDPRESS_SSH = env.get('WORDPRESS_SSH')
WORDPRESS_CLI = env.get('WORDPRESS_CLI', '/opt/wp-cli/wp')

WORDPRESS_URL = '/cms/'
