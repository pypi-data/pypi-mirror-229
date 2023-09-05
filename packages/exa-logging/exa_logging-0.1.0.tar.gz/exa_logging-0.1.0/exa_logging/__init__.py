import logging.config
import uuid

import json_log_formatter

from exa_logging.config import Config


class _JsonFormatter(json_log_formatter.JSONFormatter):
    def json_record(self, message, extra, record):
        extra.update(
            {  
                "message": message,
                "severity": record.levelname.upper(),
                "pid": record.process,
                "file": record.pathname,
                "function": record.funcName,
            }
        )
 
        if record.exc_info:
            extra["exception"] = repr(super().formatException(record.exc_info)).strip("'")
 
        try:
            if "track" not in extra:
                extra["track"] = {
                    'id': str(uuid.uuid1()),
                    'app': record.name,
                }
        except (KeyError, LookupError):
            pass
 
        return extra
  

def get_logger():
    logging.basicConfig(level=logging.DEBUG)
    logging.config.dictConfig(Config.LOG_CONFIG)
    return logging.getLogger(__name__)
