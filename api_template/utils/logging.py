import json
import logging

logger = logging.getLogger(__name__)


def log_message(action, queue_name, message=None, error=None):
    log_data = {"action": action, "queue_name": queue_name, "message": message, "error": error}
    logger.info(json.dumps(log_data))
