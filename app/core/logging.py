import logging
import json
import os
import sys
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

def setup_logging():

    if os.environ.get("TESTING") == "True":
        logging.basicConfig(
            level=logging.WARNING,  # Уменьшаем уровень логирования для тестов
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        return
    # JSON формат для логов
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    
    # File handler с ротацией
    file_handler = RotatingFileHandler(
        '/var/log/places-social/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Настройка корневого логгера
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    
    # Настройка логгеров для внешних библиотек
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
    logging.getLogger('uvicorn').setLevel(logging.INFO)
    logging.getLogger('fastapi').setLevel(logging.INFO)