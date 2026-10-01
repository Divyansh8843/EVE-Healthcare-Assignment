from fastapi import HTTPException, status


# ---------------------------------------------------------------------------
# 400 Bad Request
# ---------------------------------------------------------------------------
class BadRequestError(HTTPException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


# ---------------------------------------------------------------------------
# 401 Unauthorized
# ---------------------------------------------------------------------------
class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# ---------------------------------------------------------------------------
# 403 Forbidden
# ---------------------------------------------------------------------------
class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


# ---------------------------------------------------------------------------
# 404 Not Found
# ---------------------------------------------------------------------------
class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


# ---------------------------------------------------------------------------
# 409 Conflict
# ---------------------------------------------------------------------------
class ConflictError(HTTPException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ---------------------------------------------------------------------------
# 422 Unprocessable
# ---------------------------------------------------------------------------
class UnprocessableError(HTTPException):
    def __init__(self, detail: str = "Unprocessable entity"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )
