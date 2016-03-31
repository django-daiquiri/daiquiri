from rest_framework.parsers import BaseParser


class UWSParser(BaseParser):
    media_type = 'application/xml'
    charset = 'utf-8'
    format = 'uws'
