from typing import List
from telebot import TeleBot
from telebot.types import Message
from tg_API.common.markup_and_output import send_message_with_markup


def stop(bot: TeleBot, message: Message, menu: List, stop_message: str) -> None:
    """
    Функция stop завершает работу с ботом и закрывает меню с командами.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: menu - список с наименованиями для кнопок
    :type: List
    :param: stop_message - сообщение для вывода в чат с ботом.
    :type: str
    """
    send_message_with_markup(bot, message, stop_message, menu, number_columns=2, type_menu='Remove')
