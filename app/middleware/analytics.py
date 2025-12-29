from starlette.middleware.base import BaseHTTPMiddleware
import time
from app.services.logging.logging import get_logger

logger = get_logger(logger_name=__name__, level="INFO")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Простая middleware для логирования:
    - пути запроса
    - времени обработки
    """

    async def dispatch(self, request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = (time.time() - start_time) * 1000

        logger.info(
            f"{request.method} {request.url.path} completed in {process_time:.2f} ms "
            f"status={response.status_code}"
        )

        return response

