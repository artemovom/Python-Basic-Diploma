from typing import List, Dict, Optional, Any
from time import sleep
from json import loads
from requests import ReadTimeout, ConnectionError, ConnectTimeout
from urllib3.exceptions import ReadTimeoutError
from settings import SiteSettings
from peewee import IntegrityError, ModelSelect
from database.common.models import db
from database.core import crud, computer_components, update, history, load_data_in_model
from site_API.core import headers, params, site_api, url
from log.logging import Logging

# Общие параметры
site = SiteSettings()
# Паузы между запросами к данным API (в секундах)
query_intervals: List[int] = site.query_intervals
# Количество запрашиваемых позиций
number_requested_items: List[int] = site.number_requested_items
# Максимальное количество запросов
max_number_requests: int = site.max_number_requests

db_write = crud.create()
db_read = crud.retrieve()
db_count = crud.count()
db_delete = crud.delete()
db_save = crud.save()
db_min = crud.min_value()
db_max = crud.max_value()
db_records_in_range = crud.records_in_range()
db_records_by_single_value = crud.records_by_single_value()

# Метод для получения информации о компьютерных компонентах с сайта RapidAPI.
computer_component = site_api.get_endpoint()
# Подготовка к записи ошибок при работе с БД
logger = Logging('db', file_name='db.log').get_logger()


def _load_update_table(data: List[Dict]) -> bool:
    """
    Функция загрузки новых данных в таблицу Update базы данных.
    Существующие данные из таблицы Update предварительно удаляются.

    :param: data - список словарей с данными об обновлении таблиц базы данными.
    Ключ - наименование таблицы (модели), значение - дата следующего обновления.
    :type: List[Dict]
    :return: True, False - в случае успешной загрузки данных возвращается True, иначе False.
    :rtype: bool
    """
    try:
        db_delete(db, update['update'])
        db_write(db, update['update'], data)
        return True
    except IntegrityError as exc:
        logger.error(f"Таблица Update не заполнена\n{exc} {type(exc)}\ndb: {db}\ndata: {data}")
        return False


def _save_update_table(data: List[Dict]) -> bool:
    """
    Функция сохранения обновленных данных в таблицу Update базы данных.

    :param: data - список словарей с данными об обновлении таблиц базы данными.
    Ключ - наименование таблицы (модели), значение - дата следующего обновления.
    :type: List[Dict]
    :return: True, False - в случае успешного сохранения данных возвращается True, иначе False.
    :rtype: bool
    """
    try:
        data_model = load_data_in_model(update['update'], data)
        for i_data_model in data_model:
            db_save(db, i_data_model)
        return True
    except IntegrityError as exc:
        logger.error(f"Таблица Update не сохранена\n{exc} {type(exc)}\ndb: {db}\ndata: {data}")
        return False


def _read_update_table() -> List[Dict]:
    """
    Функция чтения всех данных из таблицы Update базы данных.

    :return: - список словарей с данными об обновлении таблицы базы данными.
    Ключ - наименование таблицы (модели), значение - дата следующего обновления.
    :rtype: List[Dict]
    """
    return db_read(db, update['update'], update['update'].id,
                   update['update'].computer_component, update['update'].update_date)


def _load_history_table(data: List[Dict]) -> bool:
    """
    Функция загрузки новых данных в таблицу History базы данных.

    :param: data - список словарей с данными об обновлении таблицы базы данными.
    Ключи - соответствуют атрибутам модели History, значения - параметры и результаты запросов.
    :type: List[Dict]
    :return: True, False - в случае успешной загрузки данных возвращается True, иначе False.
    :rtype: bool
    """
    try:
        db_write(db, history['history'], data)
        return True
    except IntegrityError as exc:
        logger.error(f"Таблица History не заполнена\n{exc} {type(exc)}\ndb: {db}\ndata: {data}")
        return False


def _read_history_table() -> List[Dict]:
    """
    Функция чтения всех данных из таблицы History базы данных.

    :return: - список словарей с данными об истории запросов.
    Ключи - соответствуют атрибутам модели History, значения - параметры и результаты запросов.
    :rtype: List[Dict]
    """
    retrieved = db_read(db, history['history'], history['history'].created_at,
                        history['history'].user_id, history['history'].command,
                        history['history'].computer_component, history['history'].price_from,
                        history['history'].price_up_to, history['history'].result)
    retrieved.order_by(history['history'].created_at.desc())

    return retrieved


def _load_data(key: str, param_offset: int = 0) -> bool:
    """
    Функция загрузки данных о компьютерных компонентах с RapidAPI в локальную базу данных.
    Существующие данные по загружаемому компоненту удаляются.

    :param: key - наименование загружаемого компонента.
    :type: str
    :param: param_offset - смещение для запроса следующих позиций.
    :type: int
    :return: result - в случае успешной загрузки данных возвращается True, иначе False.
    :rtype: bool
    """
    number_requested_items_index: int = 0
    query_interval_index: int = 0
    timeout: int = 5
    number_requests: int = 0

    result: bool = False

    while True:
        param_limit: int = number_requested_items[number_requested_items_index]
        params['limit'] = param_limit
        params['offset'] = param_offset
        try:
            response = computer_component('GET', url, headers, params, key, timeout=timeout)
        except (ReadTimeoutError, ReadTimeout, ConnectionError, ConnectTimeout) as exc:
            logger.warning(f"Ошибка запроса данных с API\n{exc} {type(exc)}\nurl: {url}\n"
                           f"headers: {headers}\nparams: {params}\nkey: {key}\ntimeout: {timeout}")
            timeout += 5
            if query_interval_index + 1 < len(query_intervals):
                query_interval_index += 1
            if timeout > 15:
                break
        else:
            if not isinstance(response, int):
                data = loads(response.text)
                for element in data:
                    element['price'] = int(element['price'] * 100)

                if not result:
                    db_delete(db, computer_components[key])

                try:
                    db_write(db, computer_components[key], data)
                except IntegrityError as exc:
                    logger.error(f"{key}: загруженные данные не сохранены в БД\n{exc} {type(exc)}\n"
                                 f"db: {db}\ndata: {data}")

                number_records = db_count(db, computer_components[key])
                query_interval_index = 0
                result = True
                param_offset = number_records
            else:
                if number_requested_items_index + 1 < len(number_requested_items):
                    number_requested_items_index += 1
                elif query_interval_index + 1 < len(query_intervals):
                    query_interval_index += 1
                else:
                    break

            number_requests += 1
            if number_requests > max_number_requests:
                break

        query_interval: int = query_intervals[query_interval_index]
        sleep(query_interval)

    return result


def _min_price(key: str, zero_values: bool = False) -> Optional[Any]:
    """
    Функция возвращает минимальную стоимость в заданной модели (таблице).

    :param: key - наименование компонента.
    :type: str
    :param: zero_values - True: возвращать нулевое значение стоимости как минимальное.
    False: нулевые значения стоимости пропускаются (по умолчанию False).
    :type: bool
    :return: - минимальная стоимость в заданной таблице.
    :rtype: Optional[Any]
    """
    return db_min(db, computer_components[key], computer_components[key].price, zero_values=zero_values)


def _max_price(key: str, zero_values: bool = False) -> Optional[Any]:
    """
    Функция возвращает максимальную стоимость в заданной модели (таблице).

    :param: key - наименование компонента.
    :type: str
    :param: zero_values - True: нулевые значения стоимости учитываются.
    False: нулевые значения стоимости пропускаются (по умолчанию False).
    :type: bool
    :return: - максимальная стоимость в заданной таблице.
    :rtype: Optional[Any]
    """
    return db_max(db, computer_components[key], computer_components[key].price, zero_values=zero_values)


def _records_in_range_by_price(key: str, min_price: Any, max_price: Any) -> ModelSelect:
    """
    Функция возвращает все записи из заданной таблицы,
    где значения цены находятся в заданном диапазоне.

    :param: key - наименование компонента.
    :type: str
    :param: min_price - минимальное значение цены.
    :type: Any
    :param: max_price - максимальное значение цены.
    :type: Any
    :return: - записи из заданной таблицы, где значения цены находятся в заданном диапазоне.
    :rtype: Optional[ModelSelect]
    """
    return db_records_in_range(db, computer_components[key], computer_components[key].price, min_price, max_price)


def _records_by_user_id(user_id: int) -> ModelSelect:
    """
    Функция возвращает все записи из таблицы History,
    где ID пользователя соответствует заданному значению.

    :param: user_id - ID пользователя.
    :type: int
    :return: - записи из таблицы History, где ID пользователя соответствует заданному значению.
    :rtype: ModelSelect
    """
    return db_records_by_single_value(db, history['history'], history['history'].user_id,
                                      user_id, history['history'].created_at, sorting_direction=True)


class ComputerComponentDatabase:
    """
    Класс ComputerComponentDatabase -
    предоставляет методы для работы с базой данных компьютерных компонентов.

    """
    @staticmethod
    def load():
        return _load_data

    @staticmethod
    def load_update_table():
        return _load_update_table

    @staticmethod
    def save_update_table():
        return _save_update_table

    @staticmethod
    def read_update_table():
        return _read_update_table

    @staticmethod
    def load_history_table():
        return _load_history_table

    @staticmethod
    def read_history_table():
        return _read_history_table

    @staticmethod
    def min_price():
        return _min_price

    @staticmethod
    def max_price():
        return _max_price

    @staticmethod
    def records_in_range_by_price():
        return _records_in_range_by_price

    @staticmethod
    def records_by_user_id():
        return _records_by_user_id


if __name__ == "__main__":
    ComputerComponentDatabase()
