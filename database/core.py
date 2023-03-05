from typing import Dict, List, TypeVar
from .utils.CRUD import CRUDInterface
from .common.models import db, ModelBase, Case, CaseFan, CpuFan, Gpu, Keyboard, Motherboard
from .common.models import Mouse, PowerSupply, Processor, Ram, Storage, Update, History

T = TypeVar("T")

# Словарь компьютерных компонентов
computer_components = {'case': Case, 'case_fan': CaseFan,
                       'cpu_fan': CpuFan, 'gpu': Gpu,
                       'keyboard': Keyboard, 'motherboard': Motherboard,
                       'mouse': Mouse, 'power_supply': PowerSupply,
                       'processor': Processor, 'ram': Ram,
                       'storage': Storage}

# Словарь таблицы истории в базе данных
history: Dict = {'history': History}

# Словарь параметров таблицы истории
history_table: Dict = {'created_at': None, 'user_id': None, 'command': None, 'computer_component': None,
                       'price_from': None, 'price_up_to': None, 'result': None}

# Словарь таблицы обновлений компьютерных компонентов в базе данных
update: Dict = {'update': Update}

db.connect()
# Создание таблиц базы данных
db.create_tables(history.values())
db.create_tables(update.values())
db.create_tables(computer_components.values())

crud = CRUDInterface()


def load_data_in_model(model: T, data: List[Dict]) -> List[T]:
    """
    Функция преобразует список словарей в список экземпляров моделей.

    :param: model - класс-модель представляемого объекта.
    :type: T
    :param: data - список словарей с данными об объекте.
    :type: List[Dict]
    :return: models - список созданных экземпляров моделей с данными из словаря.
    :rtype: List[T]
    """
    models: List[T] = list()
    for i_data in data:
        model_instance = model()
        for i_key, i_value in i_data.items():
            if hasattr(model_instance, i_key):
                setattr(model_instance, i_key, i_value)
        models.append(model_instance)
    return models


def load_model_in_json(data, *columns: str) -> List[Dict]:
    """
    Функция преобразует результаты запроса (объект ModelSelect) или
    список экземпляров моделей в список словарей с заданными полями.

    :param: data - результаты запроса (объект ModelSelect) или
    список экземпляров моделей.
    :type: ModelSelect
    :param: *columns - перечень полей, по которым данные преобразуются в список словарей.
    :type: str
    :return: data_dict - список словарей с данными результатов запроса.
    :rtype: List[Dict]
    """
    data_dict: List[Dict] = list()
    for i_element, element in enumerate(data):
        data_dict.append(dict())
        for column in columns:
            if hasattr(element, column):
                data_dict[i_element][column] = getattr(element, column)
    return data_dict


def load_columns(model: T, data: List[Dict]) -> List[ModelBase]:
    """
    Функция возвращает список атрибутов модели - столбцы таблицы в базе данных.

    :param: model - класс-модель представляемого объекта.
    :type: T
    :param: data - список словарей с данными об объекте.
    :type: List[Dict]
    :return: model_columns - список атрибутов класса-модели (столбцов таблицы в базе данных).
    :rtype: List[ModelBase]
    """
    model_columns: List[ModelBase] = list()
    for i_data in data:
        for i_key in i_data:
            if hasattr(model, i_key):
                attr: ModelBase = getattr(model, i_key)
                model_columns.append(attr)
        break
    return model_columns
