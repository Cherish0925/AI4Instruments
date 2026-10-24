"""Errors with a stable code and the information needed to continue."""


class RequestError(ValueError):
    def __init__(self, code, message, *, status=409, **details):
        super().__init__(message)
        self.code, self.status, self.details = code, status, details

    def response(self):
        return {'error': str(self), 'code': self.code, **self.details}
