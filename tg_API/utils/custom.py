from typing import Dict
from telebot import TeleBot
from telebot.types import Message
from settings import SiteSettings
from tg_API.utils.db import ComputerComponentDatabase
from tg_API.common.printing_records import price_range_request

# Общие параметры
site = SiteSettings()
# Количество одновременно выводимых в чат записей (шаг вывода)
max_number_records: int = site.max_number_records


def custom(bot: TeleBot, message: Message, parameters: Dict, name: str) -> None:
    """
    Функция custom выводит показатели пользовательского диапазона (с изображением товара).

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: name - наименование компонента для отображения в чате.
    :type: str
    """
    db_min_price = ComputerComponentDatabase.min_price()
    db_max_price = ComputerComponentDatabase.max_price()
    parameters['min_price'] = db_min_price(parameters['computer_component'])
    parameters['max_price'] = db_max_price(parameters['computer_component'])
    parameters['price_from'] = None
    parameters['price_up_to'] = None

    price_range_request(bot, message, name, parameters['min_price'], parameters['max_price'])
