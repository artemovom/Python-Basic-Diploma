from typing import List
from telebot import TeleBot
from telebot.types import Message
from tg_API.common.markup_and_output import send_message_with_markup


def start(bot: TeleBot, message: Message, menu: List, start_message: str) -> None:
    """
    Функция start выводит приглашение и меню с командами боту.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: menu - список с наименованиями для кнопок
    :type: List
    :param: start_message - сообщение для вывода в чат с ботом.
    :type: str
    """
    send_message_with_markup(bot, message, start_message, menu, number_columns=2, type_menu='Reply')
