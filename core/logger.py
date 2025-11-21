import logging
import sys
from pathlib import Path
from datetime import datetime

# Создаем папку logs если её нет
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настройка формата логирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Создаем логгер
logger = logging.getLogger("silver_car")
logger.setLevel(logging.INFO)

# Обработчик для записи в файл
file_handler = logging.FileHandler(
    LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log",
    encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

# Добавляем обработчики к логгеру
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def log_user_action(action: str, user_id: str = None, username: str = None, details: str = None):
    """Логирование действий пользователя"""
    message = f"USER ACTION: {action}"
    if user_id:
        message += f" | User ID: {user_id}"
    if username:
        message += f" | Username: {username}"
    if details:
        message += f" | Details: {details}"
    logger.info(message)

def log_system_event(event: str, details: str = None, level: str = "INFO"):
    """Логирование системных событий"""
    message = f"SYSTEM: {event}"
    if details:
        message += f" | Details: {details}"
    
    if level.upper() == "ERROR":
        logger.error(message)
    elif level.upper() == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

def log_error(error: Exception, context: str = None):
    """Логирование ошибок"""
    message = f"ERROR: {type(error).__name__}: {str(error)}"
    if context:
        message += f" | Context: {context}"
    logger.error(message, exc_info=True)

