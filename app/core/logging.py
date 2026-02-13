import logging
import json
import os
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

def setup_logging():
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )

    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)