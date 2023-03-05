from typing import Dict
from telebot import TeleBot
from telebot.types import Message
from settings import SiteSettings
from tg_API.utils.db import ComputerComponentDatabase
from tg_API.common.printing_records import request_and_output_records_by_price

# Общие параметры
site = SiteSettings()
# Количество одновременно выводимых в чат записей (шаг вывода)
max_number_records: int = site.max_number_records


def low(bot: TeleBot, message: Message, parameters: Dict, name: str) -> None:
    """
    Функция low выводит минимальные показатели (с изображением товара).

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
    parameters['min_price'] = db_min_price(parameters['computer_component'])
    parameters['max_price'] = parameters['min_price']
    parameters['price_from'] = parameters['min_price']
    parameters['price_up_to'] = parameters['min_price']

    request_and_output_records_by_price(bot, message, parameters, parameters['computer_component'], name,
                                        parameters['command'], parameters['min_price'], parameters['min_price'],
                                        parameters['start_index'], max_number_records)
