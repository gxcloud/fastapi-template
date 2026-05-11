from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ErrorResponse:
    @staticmethod
    def create(
        detail: str,
        status_code: int,
        errors: list[dict[str, str]] | None = None,
    ) -> JSONResponse:
        body: dict[str, object] = {"detail": detail, "status_code": status_code}
        if errors:
            body["errors"] = errors
        return JSONResponse(content=body, status_code=status_code)


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return ErrorResponse.create(
        detail=exc.detail,
        status_code=exc.status_code,
    )


async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return ErrorResponse.create(
        detail="Request validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        errors=[
            {
                "field": ".".join(str(x) for x in err["loc"]),
                "message": err["msg"],
            }
            for err in exc.errors()
        ],
    )


async def unhandled_exception_handler(
    _request: Request,
    exc: Exception,
) -> JSONResponse:
    from app.common.config import settings

    detail = str(exc) if settings.debug else "Internal server error"
    return ErrorResponse.create(
        detail=detail,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
