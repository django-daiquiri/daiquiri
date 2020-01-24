import daiquiri.core.env as env

TAP_SCHEMA = env.get('TAP_SCHEMA', 'tap_schema')
TAP_UPLOAD = env.get('TAP_UPLOAD', 'tap_upload')

TAP_SUBJECTS = [
    'tap'
]
