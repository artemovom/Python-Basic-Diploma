from typing import List, Optional
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


def build_menu(buttons: List, number_columns: int, header_buttons=None,
               footer_buttons=None) -> Optional[List[List]]:
    """
    Функция преобразует переданный список кнопок в список списков для построения меню из кнопок.

    :param: buttons - список кнопок.
    :type: List
    :param: number_columns - количество вложенных списков - количество колонок в меню.
    :type: int
    :param: header_buttons - верхняя кнопка.
    :type: KeyboardButton, InlineKeyboardButton
    :param: footer_buttons - нижняя кнопка.
    :type: KeyboardButton, InlineKeyboardButton
    :return: menu - список списков из кнопок.
    :rtype: Optional[List[List]]
    """
    menu = [buttons[i:i + number_columns] for i in range(0, len(buttons), number_columns)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def generate_markup(menu, number_columns: int, type_menu: str, is_numbering: bool, start_index: int):
    """
    Функция формирует меню из кнопок вида InlineKeyboardMarkup или ReplyKeyboardMarkup.

    :param: menu - словарь или список с информацией для формирования кнопок меню.
    Если вид меню InlineKeyboardMarkup - передается словарь:
    Ключ - для идентификации кнопки при нажатии, значение - для надписи на кнопке.
    Если вид меню ReplyKeyboardMarkup - передается список:
    Значения - текст для формирования кнопок, отправляющих данный текст в чат.
    :type: Dict, List
    :param: number_columns - количество колонок в меню вида InlineKeyboardMarkup.
    :type: int
    :param: type_menu - вид меню.
    'Reply' - формируется меню вида ReplyKeyboardMarkup.
    'Inline' - формируется меню вида InlineKeyboardMarkup.
    'Remove' - кнопки удаляются.
    :type: str
    :param: is_numbering - нумерация кнопок меню вида InlineKeyboardMarkup.
    True - на кнопках выводятся последовательные номера.
    False - на кнопках не выводятся последовательные номера.
    :type: bool
    :param: start_index - начальный индекс нумерации кнопок.
    :type: int
    :return: markup - сгенерированное меню кнопок.
    :rtype: ReplyKeyboardMarkup, InlineKeyboardMarkup
    """
    button_list = list()
    markup = None
    if type_menu == 'Inline':
        i_element = start_index
        for element in menu:
            if is_numbering:
                button_list.append(InlineKeyboardButton(f'{i_element}. {menu[element]}', callback_data=element))
                i_element += 1
            else:
                button_list.append(InlineKeyboardButton(f'{menu[element]}', callback_data=element))
        markup = InlineKeyboardMarkup(build_menu(button_list, number_columns))
    elif type_menu == 'Reply':
        for element in menu:
            button_list.append(KeyboardButton(element))
        markup = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True, is_persistent=True)
        if len(button_list) == 1:
            markup.row(button_list[0])
        elif len(button_list) == 2:
            markup.row(button_list[0], button_list[1])
        elif len(button_list) == 3:
            markup.row(button_list[0], button_list[1], button_list[2])
        elif len(button_list) == 4:
            markup.row(button_list[0], button_list[1], button_list[2], button_list[3])
        elif len(button_list) == 5:
            markup.row(button_list[0], button_list[1], button_list[2], button_list[3], button_list[4])
        else:
            markup.row(button_list[0])
    elif type_menu == 'Remove':
        markup = ReplyKeyboardRemove()
    return markup


def send_message_with_markup(bot: TeleBot, message: Message, text: str,
                             menu, number_columns: int = 2, type_menu: str = 'Inline',
                             is_numbering: bool = True, start_index: int = 1) -> None:
    """
    Функция отправляет сообщение в чат и выводит кнопки.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: text - текст для отправки в чат.
    :type: str
    :param: menu - словарь или список с информацией для формирования кнопок меню.
    :type: Dict, List
    :param: number_columns - количество колонок в меню вида InlineKeyboardMarkup.
    Значение по умолчанию 2.
    :type: int
    :param: type_menu - вид меню. Значение по умолчанию 'Inline'.
    'Reply' - формируется меню вида ReplyKeyboardMarkup.
    'Inline' - формируется меню вида InlineKeyboardMarkup.
    'Remove' - кнопки удаляются.
    :type: str
    :param: is_numbering - нумерация кнопок меню вида InlineKeyboardMarkup.
    True - на кнопках выводятся последовательные номера.
    False - на кнопках не выводятся последовательные номера.
    Значение по умолчанию True.
    :type: bool
    :param: start_index - начальный индекс нумерации кнопок. Значение по умолчанию 1.
    :type: int
    """
    bot.send_message(message.chat.id, text,
                     reply_markup=generate_markup(menu, number_columns, type_menu, is_numbering, start_index),
                     parse_mode='Markdown')


def edit_message_with_markup(bot: TeleBot, message: Message, text: str,
                             menu, number_columns: int = 2, type_menu: str = 'Inline',
                             is_numbering: bool = True, start_index: int = 1) -> None:
    """
    Функция редактирует сообщение в чате и выводит кнопки.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: text - текст для отправки в чат.
    :type: str
    :param: menu - словарь или список с информацией для формирования кнопок меню.
    :type: Dict, List
    :param: number_columns - количество колонок в меню вида InlineKeyboardMarkup.
    Значение по умолчанию 2.
    :type: int
    :param: type_menu - вид меню. Значение по умолчанию 'Inline'.
    'Reply' - формируется меню вида ReplyKeyboardMarkup.
    'Inline' - формируется меню вида InlineKeyboardMarkup.
    'Remove' - кнопки удаляются.
    :type: str
    :param: is_numbering - нумерация кнопок меню вида InlineKeyboardMarkup.
    True - на кнопках выводятся последовательные номера.
    False - на кнопках не выводятся последовательные номера.
    Значение по умолчанию True.
    :type: bool
    :param: start_index - начальный индекс нумерации кнопок. Значение по умолчанию 1.
    :type: int
    """
    bot.edit_message_text(text, message.chat.id, message.message_id,
                          reply_markup=generate_markup(menu, number_columns, type_menu, is_numbering, start_index),
                          parse_mode='Markdown')


def send_message(bot: TeleBot, message: Message, text: str) -> None:
    """
    Функция отправляет сообщение в чат.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: text - текст для отправки в чат.
    :type: str
    """
    bot.send_message(message.chat.id, text, parse_mode='Markdown')


def send_photo(bot: TeleBot, message: Message, photo, caption: str) -> None:
    """
    Функция отправляет картинку с надписью в чат.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: photo - загруженная картинка.
    :type:
    :param: caption - текст для надписи.
    :type: str
    """
    bot.send_photo(message.chat.id, photo, caption, parse_mode='Markdown')
