from typing import List
from os import getenv
from dotenv import load_dotenv
from pydantic import BaseSettings, SecretStr, StrictStr

load_dotenv()


class SiteSettings(BaseSettings):
    """
    Класс SiteSettings - обеспечивает доступ к общим параметрам.
    Родитель: BaseSettings

    Attributes:
    api_key (SecretStr): Ключ RapidAPI
    host_api (StrictStr): Хост API
    token (SecretStr): Токен телеграм бота
    db_path (StrictStr): Путь к базе данных
    db_update_frequency (int): Частота обновления базы данных (в днях)
    query_intervals (List[int]): Паузы между запросами к данным API (в секундах)
    number_requested_items (List[int]): Количество запрашиваемых позиций
    max_number_requests (int): Максимальное количество запросов
    max_number_records (int): Максимальное количество записей, выводимых в чат (одновременно, шаг вывода)
    folder_log (StrictStr): Наименование папки с логом
    logging_config_file (StrictStr): Наименование конфигурационного файла
    """
    api_key: SecretStr = getenv("SITE_API", None)
    host_api: StrictStr = getenv("HOST_API", None)
    token: SecretStr = getenv("TELEGRAM_TOKEN", None)
    db_path: StrictStr = getenv("DB_PATH", None)
    db_update_frequency: int = getenv("DB_UPDATE_FREQUENCY", None)
    query_intervals: List[int] = getenv("QUERY_INTERVALS", None)
    number_requested_items: List[int] = getenv("NUMBER_REQUESTED_ITEMS", None)
    max_number_requests: int = getenv("MAX_NUMBER_REQUESTS", None)
    max_number_records: int = getenv("MAX_NUMBER_RECORDS", None)
    folder_log: StrictStr = getenv("FOLDER_LOG", None)
    logging_config_file: StrictStr = getenv("LOGGING_CONFIG_FILE", None)
