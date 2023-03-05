from typing import List, Dict
from telebot import TeleBot
from telebot.types import Message
from settings import SiteSettings
from tg_API.common.printing_records import read_and_output_history

# Общие параметры
site = SiteSettings()
# Количество одновременно выводимых в чат записей (шаг вывода)
max_number_records: int = site.max_number_records


def history(bot: TeleBot, message: Message, menu: Dict, parameters: Dict, history_info: List[Dict]) -> None:
    """
    Функция history выводит истории запросов пользователей.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: menu - словарь для формирования кнопок меню.
    Ключ - для идентификации кнопки при нажатии, значение - для надписи на кнопке.
    :type: Dict
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: history_info - список словарей с информацией по истории запросов.
    :type: List[Dict]
    """
    read_and_output_history(bot, message, menu, parameters, max_number_records, history_info)
