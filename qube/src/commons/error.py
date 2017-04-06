from enum import IntEnum


class TestServiceError(Exception):
    def __init__(self, message, errors):
        # Call the base class constructor with the parameters it needs
        super(TestServiceError, self).__init__(message)

        # Now for your custom code...
        self.errors = errors


class ErrorCodes(IntEnum):
    NOT_FOUND = 404
    NOT_ALLOWED = 2
    MISSING_REQUIRED = 400
    SERVER_ERROR = 500
    UNAUTHORIZED = 401
    ALREADY_EXIST = 409
    NOT_SUPPORTED = 400
