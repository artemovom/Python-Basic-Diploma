from telebot import TeleBot
from telebot.types import Message


def help_on_commands(bot: TeleBot, message: Message, help_message: str) -> None:
    """
    Функция help_on_commands выводит подсказку по командам бота.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: help_message - сообщение для вывода в чат с ботом.
    :type: str
    """
    bot.send_message(message.chat.id, help_message)
