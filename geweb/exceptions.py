class HTTPError(Exception):
    code = 555
    message = "Unknown HTTP Error"

class BadRequest(HTTPError):
    code = 400
    message = "Bad Request"

class Forbidden(HTTPError):
    code = 403
    message = "Forbidden"

class NotFound(HTTPError):
    code = 404
    message = "Page Not Found"

class MethodNotAllowed(HTTPError):
    code = 405
    message = "Method Not Allowed"

class InternalServerError(HTTPError):
    code = 500
    message = "Internal Server Error"

