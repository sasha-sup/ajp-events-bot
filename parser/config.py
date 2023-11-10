import logging
import os

DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')


URL = "https://ajptour.com/en/events-1/events-calendar-2023-2024"

# log
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(
    format=log_format,
    level=logging.INFO,
    filename="/app/log/main.log")
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
