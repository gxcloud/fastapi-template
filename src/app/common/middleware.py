import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        start = time.perf_counter()
        response = await call_next(request)
        duration = (time.perf_counter() - start) * 1000

        logger.info(
            "%s %s %s %dms [%s]",
            request.method,
            request.url.path,
            response.status_code,
            int(duration),
            request_id,
        )
        response.headers["X-Request-ID"] = request_id
        return response
