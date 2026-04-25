import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

import os
from pathlib import Path

def setup_logging():
    """Setup logging configuration"""
    logger = logging.getLogger('rag_system')
    logger.setLevel(logging.INFO)
    
    # Ensure logs directory exists
    Path('logs').mkdir(parents=True, exist_ok=True)
    
    # File handler
    file_handler = logging.FileHandler('logs/rag_system.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger
