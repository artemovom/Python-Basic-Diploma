from typing import Dict, List, TypeVar, Optional, Any
from peewee import ModelSelect, fn
from ..common.models import ModelBase
from ..common.models import db

T = TypeVar("T")


def _store_data(database: db, model: T, *data: List[Dict]) -> None:
    """
    Функция сохранения в базу данных.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта.
    :type: T
    :param: data - список словарей с данными объекта.
    :type: List[Dict]
    """
    with database.atomic():
        model.insert_many(*data).execute()


def _retrieve_all_data(database: db, model: T, *columns: ModelBase) -> ModelSelect:
    """
    Функция чтения данных из базы. Возвращаются все записи по заданным столбцам.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта.
    :type: T
    :param: columns - столбцы по которым возвращаются данные из базы (атрибуты модели).
    :type: ModelSelect
    """
    with database.atomic():
        response = model.select(*columns)

    return response


def _counting_records(database: db, model: T) -> int:
    """
    Функция возвращает количество записей в заданной таблице.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    :return: response - количество записей в заданной таблице базы данных.
    :rtype: int
    """
    with database.atomic():
        response = model.select().count()

    return response


def _min_value(database: db, model: T, column: ModelBase, zero_values: bool) -> Optional[Any]:
    """
    Функция возвращает минимальное значение в заданной таблице по заданному полю.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    :param: column - столбец по которому возвращается минимальное значение.
    :type: ModelBase
    :param: zero_values - True: нулевые значения стоимости учитываются.
    False: нулевые значения стоимости пропускаются.
    :type: bool
    :return: response - минимальное значение в заданной таблице по заданному полю.
    :rtype: Optional[Any]
    """
    with database.atomic():
        if zero_values:
            response = model.select(fn.Min(column)).scalar()
        else:
            response = model.select().where(column > 0)
            response = response.select(fn.Min(column)).scalar()

    return response


def _max_value(database: db, model: T, column: ModelBase, zero_values: bool) -> Optional[Any]:
    """
    Функция возвращает максимальное значение в заданной таблице по заданному полю.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    :param: column - столбец по которому возвращается максимальное значение.
    :type: ModelBase
    :param: zero_values - True: нулевые значения стоимости учитываются.
    False: нулевые значения стоимости пропускаются.
    :return: response - максимальное значение в заданной таблице по заданному полю.
    :rtype: Optional[Any]
    """
    with database.atomic():
        if zero_values:
            response = model.select(fn.Max(column)).scalar()
        else:
            response = model.select().where(column > 0)
            response = response.select(fn.Max(column)).scalar()

    return response


def _records_in_range(database: db, model: T, column: ModelBase,
                      min_value: Any, max_value: Any) -> ModelSelect:
    """
    Функция возвращает все записи из заданной таблицы,
    где значения по заданному столбцу находятся в заданном диапазоне.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    :param: column - столбец по которому возвращается максимальное значение.
    :type: ModelBase
    :param: min_value - минимальное значение по заданному столбцу.
    :type: Any
    :param: max_value - максимальное значение по заданному столбцу.
    :type: Any
    :return: response - записи из заданной таблицы, где значения по заданному столбцу находятся в заданном диапазоне.
    :rtype: Optional[ModelSelect]
    """
    with database.atomic():
        response = model.select().where((column >= min_value) & (column <= max_value)).order_by(column)

    return response


def _records_by_single_value(database: db, model: T, column: ModelBase,
                             value: Any, column_order_by: ModelBase,
                             sorting_direction: bool = False) -> ModelSelect:
    """
    Функция возвращает все записи из заданной таблицы,
    где значения по заданному столбцу совпадают с заданным значением.
    Найденные записи сортируются по заданному столбцу.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    :param: column - столбец по которому выполняется поиск.
    :type: ModelBase
    :param: value - искомое значение значение по заданному столбцу.
    :type: Any
    :param: column_order_by - столбец по которому выполняется сортировка.
    :type: ModelBase
    :param: sorting_direction - направление сортировки.
    True - по возрастанию (по умолчанию). False - по убыванию.
    :type: bool
    :return: response - записи из заданной таблицы, где значения по заданному столбцу находятся в заданном диапазоне.
    :rtype: Optional[ModelSelect]
    """
    with database.atomic():
        if sorting_direction:
            response = model.select().where(column == value).order_by(column_order_by.desc())
        else:
            response = model.select().where(column == value).order_by(column_order_by)
    return response


def _delete_all_data(database: db, model: T) -> None:
    """
    Функция удаляет все записи в заданной таблице.

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    """
    with database.atomic():
        model.delete().execute()


def _update_data(database: db, model: T, data: List[ModelBase], columns: List[ModelBase]) -> int:
    """
    Функция обновляет (сохраняет) несколько записей в базе данных.
    Данные передаются в виде списка экземпляров классов-моделей.
    Данные сохраняются в указанных столбцах (атрибуты моделей).

    :param: database - база данных.
    :type: db
    :param: model - модель объекта (таблица базы данных).
    :type: T
    :param: data - список экземпляров классов-моделей с сохраняемыми данными.
    :type: List[ModelBase]
    :param: columns - список столбцов по которым сохраняются данные (атрибуты моделей).
    :type: List[ModelBase]
    :return: response - количество обновленных (сохраненных) записей в базу данных.
    :rtype: int
    """
    with database.atomic():
        response = model.bulk_update(data, columns)

    return response


def _save_data(database: db, model: ModelBase) -> int:
    """
    Функция сохраняет одну запись в базу данных.
    Данные передаются в виде экземпляра класса-модели.
    Данные сохраняются по всем столбцам (атрибутам) модели.

    :param: database - база данных.
    :type: db
    :param: model - экземпляр класса-модели с сохраняемыми данными.
    :type: ModelBase
    :return: response - количество сохраненных записей в базу данных.
    :rtype: int
    """
    with database.atomic():
        response = model.save()

    return response


class CRUDInterface:
    """
    Класс CRUDInterface - предоставляет методы для работы с базой данных:
    создание, чтение, модификация, удаление, поиск минимального и максимального значений,
    возврат записей по заданным критериям

    """
    @staticmethod
    def create():
        return _store_data

    @staticmethod
    def retrieve():
        return _retrieve_all_data

    @staticmethod
    def count():
        return _counting_records

    @staticmethod
    def delete():
        return _delete_all_data

    @staticmethod
    def update():
        return _update_data

    @staticmethod
    def save():
        return _save_data

    @staticmethod
    def min_value():
        return _min_value

    @staticmethod
    def max_value():
        return _max_value

    @staticmethod
    def records_in_range():
        return _records_in_range

    @staticmethod
    def records_by_single_value():
        return _records_by_single_value


if __name__ == "__main__":
    CRUDInterface()
