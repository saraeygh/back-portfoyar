import time
import logging
import logging.handlers

from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent.parent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    f"{CODE_DIR}/logs/request_response_duration_logger_middleware.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class RequestResponseDurationLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        t_start = time.time()

        response = self.get_response(request)

        t_end = time.time()

        logger.info(f"{request.method} - {request.path} - {t_end - t_start}")

        return response
