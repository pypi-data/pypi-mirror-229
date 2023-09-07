from typing import TypedDict
from . import schemas

HTTP_ERRORS = {
    422: schemas.RequestValidationError,
    409: schemas.ConflictError,
    401: schemas.UnauthorizedError,
    404: schemas.NotFoundError,
    500: TypedDict("InternalServerError", {"detail": str}),
}


def get_error_class(status_code: int):
    if status_code in HTTP_ERRORS:
        return HTTP_ERRORS.get(status_code)
    else:
        raise ValueError(f"Status code no in schemas: {status_code}")
