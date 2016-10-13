from daiquiri_core.exceptions import DaiquiriException


class ADQLSyntaxError(DaiquiriException):
    pass


class MySQLSyntaxError(DaiquiriException):
    pass


class PermissionError(DaiquiriException):
    pass
