from typing import List, Dict, Optional, Any
from time import sleep
from datetime import datetime, date, timedelta
from threading import Thread
from settings import SiteSettings
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from tg_API.utils.custom import custom
from tg_API.utils.db import ComputerComponentDatabase
from tg_API.utils.help import help_on_commands
from tg_API.utils.high import high
from tg_API.utils.history import history
from tg_API.utils.low import low
from tg_API.utils.start import start
from tg_API.utils.stop import stop
from tg_API.common.markup_and_output import send_message_with_markup, send_message
from tg_API.common.printing_records import price_range_read, output_records, output_records_history
from database.core import computer_components, update, crud
from database.common.models import db
from log.logging import Logging

# Сообщение о боте
ABOUT_BOT = "Я бот @ComputerComponentsBot\n" \
            "Могу предоставить информацию по компьютерным компонентам:\n" \
            " - стоимости\n" \
            " - основным параметрам\n" \
            "/start - показать меню\n" \
            "/help - справка по командам\n" \

# Справка по командам бота
BOT_COMMAND = "/start - показать меню\n" \
              "/help - справка по командам\n" \
              "/low - вывод компонентов с минимальной стоимостью\n" \
              "/high - вывод компонентов с максимальной стоимостью\n" \
              "/custom - вывод компонентов со стоимостью из заданного диапазона\n" \
              "/history - вывод истории запросов\n" \
              "/stop - закрыть меню"

# Словарь с параметрами запроса: заданной команды, выбранного компьютерного компонента, диапазоном цен
# начального индекса вывода найденных записей, начального индекса вывода записей истории, ключ нажатой кнопки
request_parameters: Dict = {'command': None, 'computer_component': None,
                            'min_price': None, 'max_price': None,
                            'price_from': None, 'price_up_to': None, 'start_index': 1,
                            'start_index_button': 1, 'key_button': None}

# Словарь команд
commands: Dict = {'custom': custom, 'help': help_on_commands, 'high': high,
                  'history': history, 'low': low, 'start': start, 'stop': stop}

# Словарь функций
function_commands: Dict = {'custom': None, 'help': None, 'high': None,
                           'history': None, 'low': None, 'start': None, 'stop': None}

# Словарь наименований команд для отображения
names_commands: Dict = {'low': 'Мин. цене', 'high': 'Макс. цене', 'custom': 'Диапазону цен'}

# Список команд для меню
menu_commands = ['Команды', 'Компоненты', 'История', 'Справка', 'Завершить']

# Словарь наименований компьютерных компонентов для отображения
names_computer_components: Dict[str, str] = {key: str(model()) for key, model in computer_components.items()}

# Список словарей с информацией по истории запросов
# Ключи словаря:
# created_at - дата запроса
# user_id - id пользователя
# command - команда
# computer_component - выбранный компьютерный компонент
# price_from - цена от
# price_up_to - цена до
# result - результат запроса
history_info: List[Dict] = list()

# Общие параметры
site = SiteSettings()
# Телеграм бот
bot = TeleBot(site.token.get_secret_value())
# Частота обновления базы данных (в днях)
db_update_frequency: int = site.db_update_frequency
# Количество одновременно выводимых в чат записей (шаг вывода)
max_number_records: int = site.max_number_records
# Подготовка к записи ошибок в лог файл
logger = Logging('main').get_logger()


@bot.message_handler(commands=['custom'])
def output_custom_values(message: Message) -> None:
    """
    Функция по команде /custom выводит показатели пользовательского диапазона (с изображением товара).

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    request_parameters['command'] = 'custom'
    reset_request_parameters(request_parameters, 'computer_component', 'min_price', 'max_price',
                             'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                             start_index='start_index', start_index_button='start_index_button')
    send_message_with_markup(bot, message, 'Выберите компонент:', names_computer_components)


@bot.message_handler(commands=['help'])
def help_on_bot_commands(message: Message) -> None:
    """
    Функция по команде /help выводит подсказку по командам бота.

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    help_on_commands(bot, message, BOT_COMMAND)


@bot.message_handler(commands=['high'])
def output_high_values(message: Message) -> None:
    """
    Функция по команде /high выводит максимальные показатели (с изображением товара).

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    request_parameters['command'] = 'high'
    reset_request_parameters(request_parameters, 'computer_component', 'min_price', 'max_price',
                             'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                             start_index='start_index', start_index_button='start_index_button')
    send_message_with_markup(bot, message, 'Выберите компонент:', names_computer_components)


@bot.message_handler(commands=['history'])
def output_history(message: Message) -> None:
    """
    Функция по команде /history выводит историю запросов пользователя.

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    request_parameters['command'] = 'history'
    reset_request_parameters(request_parameters, 'computer_component', 'min_price', 'max_price',
                             'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                             start_index='start_index', start_index_button='start_index_button')
    history(bot, message, names_computer_components, request_parameters, history_info)


@bot.message_handler(commands=['low'])
def output_low_values(message: Message) -> None:
    """
    Функция по команде /low выводит минимальные показатели (с изображением товара).

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    request_parameters['command'] = 'low'
    reset_request_parameters(request_parameters, 'computer_component', 'min_price', 'max_price',
                             'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                             start_index='start_index', start_index_button='start_index_button')
    send_message_with_markup(bot, message, 'Выберите компонент:', names_computer_components)


@bot.message_handler(commands=['start'])
def output_start_message(message: Message) -> None:
    """
    Функция по команде /start выводит приглашение и меню с командами боту.

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    reset_request_parameters(request_parameters, 'command', 'computer_component',
                             'min_price', 'max_price',
                             'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                             start_index='start_index', start_index_button='start_index_button')
    start(bot, message, menu_commands, 'Готов выполнить Ваш запрос! Начните с выбора команды.')


@bot.message_handler(commands=['stop'])
def output_stop_message(message: Message) -> None:
    """
    Функция по команде /stop завершает работу с ботом и закрывает меню с командами.

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    reset_request_parameters(request_parameters, 'command', 'computer_component',
                             'min_price', 'max_price',
                             'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                             start_index='start_index', start_index_button='start_index_button')
    stop(bot, message, menu_commands, 'Пока. До новых запросов.')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call: CallbackQuery) -> None:
    """
    Функция обрабатывает нажатие кнопок в чате.

    :param: call - объект из telebot, содержащий информацию о сообщении, о нажатой кнопке.
    :type: CallbackQuery
    """
    if call.message:
        key = str(call.data)
        if key in names_commands.keys():
            function_commands[key](call.message)
        # Выбор компьютерного компонента
        elif key in names_computer_components.keys():
            if request_parameters['command'] in names_commands.keys():
                name: str = names_computer_components[key]
                request_parameters['computer_component'] = key
                reset_request_parameters(request_parameters, 'min_price', 'max_price', 'price_from',
                                         'price_up_to', 'start_index', 'start_index_button', 'key_button',
                                         start_index='start_index', start_index_button='start_index_button')
                db_command = commands[request_parameters['command']]
                db_command(bot, call.message, request_parameters, name)
            else:
                bot.send_message(call.message.chat.id, 'Сначала выберите команду')
                send_message_with_markup(bot, call.message, 'Поиск компонентов по:', names_commands)
        # Выбор одной записи из истории запросов пользователя
        elif is_int(key):
            key = int(key)
            if request_parameters['command'] == 'history':
                request_parameters['key_button'] = key
                request_parameters['start_index'] = 1
                output_records_history(bot, call.message, names_computer_components, request_parameters,
                                       max_number_records, history_info)
        # Вывод следующих записей по найденным компьютерным компонентам
        elif key == 'next_output':
            if (request_parameters['command'] in names_commands.keys() and
                    request_parameters['computer_component'] in names_computer_components.keys() and
                    request_parameters['min_price'] and request_parameters['max_price'] and
                    request_parameters['price_from'] and request_parameters['price_up_to'] and
                    request_parameters['start_index'] > 1):
                db_records_by_price = ComputerComponentDatabase.records_in_range_by_price()
                records_by_price = db_records_by_price(request_parameters['computer_component'],
                                                       request_parameters['price_from'],
                                                       request_parameters['price_up_to'])
                output_records(bot, call.message, request_parameters,
                               names_computer_components[request_parameters['computer_component']],
                               request_parameters['command'], request_parameters['price_from'],
                               request_parameters['price_up_to'], request_parameters['start_index'],
                               max_number_records, records_by_price)
            elif request_parameters['command'] == 'history' and request_parameters['key_button'] and \
                    request_parameters['start_index_button'] > 1:
                output_records_history(bot, call.message, names_computer_components, request_parameters,
                                       max_number_records, history_info)
        # Вывод следующих записей из истории запросов пользователя
        elif key == 'next_records_history':
            if request_parameters['command'] == 'history' and request_parameters['start_index_button'] > 1:
                history(bot, call.message, names_computer_components, request_parameters, history_info)

        else:
            logger.warning(f'Неожиданная команда {key}\n{request_parameters}')
            bot.send_message(call.message.chat.id, f'Неожиданная команда {key}\nВыберите другую команду')
            reset_request_parameters(request_parameters, 'command', 'computer_component',
                                     'min_price', 'max_price',
                                     'price_from', 'price_up_to', 'start_index', 'start_index_button', 'key_button',
                                     start_index='start_index', start_index_button='start_index_button')
            send_message_with_markup(bot, call.message, 'Поиск компонентов по:', names_commands)


@bot.message_handler(content_types=["text"])
def text_query(message: Message) -> None:
    """
    Функция обрабатывает сообщения из чата от пользователя и в случае соответствия одной из команд,
    запускает соответствующую процедуру.
    Основные команды сохранены в словаре menu_commands

    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    """
    # Приветствие. Вывод сообщения о боте.
    if message.text.lower().startswith('привет'):
        bot.send_message(message.chat.id, ''.join(("Привет! ", ABOUT_BOT)))
    elif message.text == menu_commands[0]:
        # Команды
        send_message_with_markup(bot, message, 'Поиск компонентов по:', names_commands)
    elif message.text == menu_commands[1]:
        # Компоненты
        if request_parameters['command'] in names_commands.keys():
            send_message_with_markup(bot, message, 'Выберите компонент:', names_computer_components)
        else:
            bot.send_message(message.chat.id, 'Сначала выберите команду')
            send_message_with_markup(bot, message, 'Поиск компонентов по:', names_commands)
    elif message.text == menu_commands[2]:
        # История
        function_commands['history'](message)
    elif message.text == menu_commands[3]:
        # Справка по командам
        function_commands['help'](message)
    elif message.text == menu_commands[4]:
        # Завершить
        function_commands['stop'](message)
    elif request_parameters['command'] == 'custom' and request_parameters['computer_component']:
        # Запрос ввода диапазона цен
        price_range_read(bot, message, request_parameters, message.text,
                         names_computer_components[request_parameters['computer_component']],
                         request_parameters['start_index'], max_number_records)
    else:
        send_message(bot, message, 'Не понял Вашу команду\n/help - справка по командам')


def database_loading() -> None:
    """
    Функция периодически (1 раз в сутки) производит проверку таблицы Update
    и обновляет информацию о компьютерных компонентах с сайта rapidAPI.

    """
    db_read_update_table = ComputerComponentDatabase.read_update_table()
    db_save_update_table = ComputerComponentDatabase.save_update_table()
    db_load = ComputerComponentDatabase.load()
    db_count = crud.count()

    # Заполнение таблицы Update в базе
    if not db_count(db, update['update']) == len(computer_components):
        db_load_update_table = ComputerComponentDatabase.load_update_table()
        update_table = list()
        i_date: date = datetime.now().date()
        for key in computer_components.keys():
            i_date += timedelta(days=1)
            update_table.append({'computer_component': key, 'update_date': i_date})
        db_load_update_table(update_table)

    while True:
        update_table = db_read_update_table()

        date_now: date = datetime.now().date()
        for element in update_table:
            if date_now >= element.update_date:
                computer_component: str = element.computer_component
                if db_load(computer_component):
                    number_records = db_count(db, computer_components[computer_component])
                    logger.info(f'{computer_component}: данные с API успешно загружены. '
                                f'Дата обновления {date_now}. Количество записей в БД {number_records}.')
                    element.update_date = date_now + timedelta(days=db_update_frequency)
                    update_table_dict = [{'id': element.id, 'computer_component': element.computer_component,
                                          'update_date': element.update_date}]
                    db_save_update_table(update_table_dict)
                else:
                    number_records = db_count(db, computer_components[computer_component])
                    logger.warning(f'{computer_component}: ошибка загрузки данных API. '
                                   f'Дата последнего обновления {element.update_date}. '
                                   f'Количество записей в БД {number_records}.')
        sleep(86400)


def reset_request_parameters(parameters: Dict, *key: str, start_index: str = 'start_index',
                             start_index_button: str = 'start_index_button') -> None:
    """
    Функция устанавливает значение 'None' указанных ключей словаря.
    В двух именованных параметрах передаются ключи, значения которых приводятся к 1.

    :param: parameters - словарь.
    :type: Dict
    :param: *key - ключи словаря, значения которых требуется привести к исходным данным
    :type: str
    :param: start_index - ключ словаря для установки начального индекса вывода записей к 1.
    :type: str
    :param: start_index_button - ключ словаря для установки начального индекса выводимой кнопки меню к 1.
    :type: str
    """
    for i_key in key:
        if i_key == start_index or i_key == start_index_button:
            parameters[i_key] = 1
        else:
            parameters[i_key] = None


def is_int(value: Optional[Any]) -> bool:
    """
    Функция определяет, может ли переданное значение быть преобразовано к целочисленному типу данных.

    :param: value - наименование загружаемого компонента.
    :type: Optional[Any]
    :return: - в случае успешного преобразования к целочисленному типу данных возвращается True,
    иначе False.
    :rtype: bool
    """
    try:
        int(value)
        return True
    except ValueError:
        return False


class TelegramBot:
    """
    Класс TelegramBot - предоставляет метод для запуска телеграм бота.

    """
    @staticmethod
    def run():
        function_commands['custom'] = output_custom_values
        function_commands['help'] = help_on_bot_commands
        function_commands['high'] = output_high_values
        function_commands['history'] = output_history
        function_commands['low'] = output_low_values
        function_commands['start'] = output_start_message
        function_commands['stop'] = output_stop_message
        Thread(target=database_loading).start()
        bot.infinity_polling()


if __name__ == '__main__':
    bot.infinity_polling()
