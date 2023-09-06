class BadPacketHeader(ValueError):
    ...


class HeartbeatError(ValueError):
    ...


class BadResponse(ValueError):
    ...


class ResponseError(RuntimeError):
    ...


class BadRequest(ResponseError):
    ...


class Unauthorized(ResponseError):
    ...


class NotFound(ResponseError):
    ...


class MethodNotAllowed(ResponseError):
    ...


class RequestTimeout(ResponseError):
    ...


class InternalServerError(ResponseError):
    ...
