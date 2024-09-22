import logging
import logging.handlers

from pathlib import Path

CODE_DIR = Path(__file__).resolve().parent.parent.parent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.handlers.RotatingFileHandler(
    f"{CODE_DIR}/non_20x_status_response_logger_middleware.log",
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)


class Non20xStatusResponseLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not 200 <= response.status_code < 300:
            logger.info(
                "REQUEST = {"
                f"method: {request.method}, "
                f"user: {request.user.username}, "
                f"url: {request.path}, "
                # f"body: {request.body}"
                "}"
                " - RESPONSE = {"
                f"status: {response.status_code}, "
                "}"
            )

        return response
