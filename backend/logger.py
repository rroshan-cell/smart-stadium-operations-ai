import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime
from .config import settings

def setup_logger():
    logger = logging.getLogger("smart_stadium")
    logger.setLevel(settings.LOG_LEVEL)
    
    handler = logging.StreamHandler(sys.stdout)
    
    class StructuredFormatter(logging.Formatter):
        def format(self, record: logging.LogRecord) -> str:
            log_record: Dict[str, Any] = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "message": record.getMessage(),
                "module": record.module,
                "request_id": getattr(record, "request_id", None)
            }
            if record.exc_info:
                log_record["exception"] = self.formatException(record.exc_info)
            return json.dumps(log_record)

    handler.setFormatter(StructuredFormatter())
    logger.addHandler(handler)
    return logger

logger = setup_logger()
