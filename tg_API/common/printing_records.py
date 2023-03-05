from typing import List, Dict
from copy import deepcopy
from datetime import datetime
from requests import get
from telebot import TeleBot
from telebot.types import Message
from tg_API.common.markup_and_output import send_message, send_photo, send_message_with_markup
from tg_API.utils.db import ComputerComponentDatabase
from database.core import load_model_in_json, history_table, computer_components, load_data_in_model
from log.logging import Logging

# Подготовка к записи ошибок в лог файл
logger = Logging('main').get_logger()


def convert_records_to_string(records, start_index: int,
                              max_index: int, *columns: str, is_numbering: bool = True,
                              link: str = 'link', img: str = 'img', price: str = 'price') -> List[Dict[str, str]]:
    """
    Функция преобразует результаты запроса к базе данных в список словарей с текстовыми значениями,
    для последующего вывода в чат.

    :param: records - записи по результатам запроса к базе данных
    :type: ModelSelect
    :param: start_index - начальный индекс элемента с которого начинается преобразование в строку.
    :type: int
    :param: max_index - максимальное количество преобразуемых элементов (шаг).
    :type: int
    :param: *columns - перечень полей, по которым данные преобразуются с строку.
    :type: str
    :param: is_numbering - нумерация записей (по умолчанию True).
    Если True, то преобразуемые записи нумеруются, если False - не нумеруются.
    :type: bool
    :param: link - ссылка на компонент в интернет-магазине.
    :type: str
    :param: img - ссылка на изображение компонента.
    :type: str
    :param: price - цена компонента.
    :type: str
    :return: result - данные запроса преобразованные в список строк.
    :rtype: List[Dict[str, str]]
    """
    result: List[Dict[str, str]] = []
    end_index: int = start_index + max_index - 1
    for i_element, element in enumerate(records, 1):
        if start_index <= i_element <= end_index:
            numbering: str = ''
            record: str = ''
            previous_record: str = ''
            img_link: str = ''
            if is_numbering:
                numbering = f'{i_element}. '
            for column in columns:
                if hasattr(element, column):
                    current_record: str = str(getattr(element, column))
                    if column == link:
                        record = record.replace(f'{previous_record}; ', f'[{previous_record}]')
                        record = ''.join((record, f'({current_record}); '))
                    elif column == price:
                        try:
                            current_record = f'{int(current_record) / 100}$'
                        except ValueError:
                            pass
                        record = ''.join((record, f'{current_record}; '))
                    elif column == img:
                        img_link = current_record
                    else:
                        current_record = current_record.replace('[', '(')
                        current_record = current_record.replace(']', ')')
                        record = ''.join((record, f'{current_record}; '))
                    previous_record = current_record
            if record.endswith('; '):
                record = record[:len(record) - 2]
            record = ''.join((numbering, record, '\n'))
            result.append({'text': record, 'img': img_link})
        elif i_element > end_index:
            break

    return result


def output_records(bot: TeleBot, message: Message, parameters: Dict, name: str, command: str,
                   min_price: int, max_price: int, start_index: int, max_index: int,
                   records_by_price) -> bool:
    """
    Функция выводит в чат результаты запроса к БД.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: name - наименование компонента для отображения в чате.
    :type: str
    :param: command - выбранная команда.
    :type: str
    :param: min_price - минимальная цена компонента (левая граница диапазона цен).
    :type: int
    :param: max_price - максимальная цена компонента (правая граница диапазона цен).
    :type: int
    :param: start_index - начальный индекс элемента с которого начинается вывод результатов запроса.
    :type: int
    :param: max_index - максимальное количество одновременно выводимых элементов.
    :type: int
    :param: records_by_price - записи по результатам запроса к базе данных
    :type: ModelSelect
    :return: True - успешный вывод записей в чат.
    False - получены не все данные (обрабатываемые исключения).
    :rtype: bool
    """
    if isinstance(min_price, int) and isinstance(max_price, int):
        text: str = ''
        if command == 'low':
            text = f'{name}: минимальная цена {min_price / 100}$\n'
        elif command == 'high':
            text = f'{name}: максимальная цена {max_price / 100}$\n'
        elif command == 'custom':
            text = f"{name}: цена от {min_price / 100}$ до {max_price / 100}$\n"

        records_count: int = len(records_by_price)
        if records_count > 0:
            send_message(bot, message, text)
            records = convert_records_to_string(records_by_price,
                                                start_index, max_index,
                                                'title', 'link', 'price', 'img')
            for i_records in records:
                photo = get(i_records['img'])
                if photo.status_code == 200:
                    send_photo(bot, message, photo.content, i_records['text'])
                else:
                    logger.warning(f'Изображение не загружено, код {photo.status_code}\n{i_records}')
                    send_message(bot, message, i_records['text'])

            start_index = start_index + max_index
            end_index: int = start_index + max_index - 1

            if start_index <= records_count:
                if end_index > records_count:
                    end_index = records_count
                menu_next_output = {'next_output': f'с {start_index} по {end_index} (всего {records_count})'}
                send_message_with_markup(bot, message, 'Следующие записи:', menu_next_output,
                                         number_columns=1, is_numbering=False)
                parameters['start_index'] = start_index
            else:
                parameters['start_index'] = 1
                parameters['key_button'] = None

            return True
        else:
            result = ''.join((text, 'Записи не найдены'))
            send_message(bot, message, result)
            logger.warning(f'Записи не найдены: {name}; {command}; {min_price}; {max_price}; {start_index}; '
                           f'{max_index}\n{parameters}\n{records_by_price}')
            return False

    else:
        send_message(bot, message, f'{name}\nЦены не заданы')
        logger.warning(f'Цены не заданы: {name}; {command}; {min_price}; {max_price}; {start_index}; '
                       f'{max_index}\n{parameters}\n{records_by_price}')
    return False


def request_and_output_records_by_price(bot: TeleBot, message: Message, parameters: Dict,
                                        key: str, name: str, command: str, min_price: int,
                                        max_price: int, start_index: int, max_index: int) -> bool:
    """
    Функция запрашивает записи в БД по заданному диапазону цен и выводит результаты в чат.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: key - выбранный компьютерный компонент.
    :type: str
    :param: name - наименование компонента для отображения в чате.
    :type: str
    :param: command - выбранная команда.
    :type: str
    :param: min_price - минимальная цена компонента (левая граница диапазона цен).
    :type: int
    :param: max_price - максимальная цена компонента (правая граница диапазона цен).
    :type: int
    :param: start_index - начальный индекс элемента с которого начинается вывод результатов запроса.
    :type: int
    :param: max_index - максимальное количество одновременно выводимых элементов.
    :type: int
    :return: True - успешное выполнение запроса и вывод записей в чат.
    False - запрос к БД и вывод записей в чат завершился обработкой исключений
    (отсутствуют записи в базе данных по заданным условиям).
    :rtype: bool
    """
    records_by_price = None
    if isinstance(min_price, int) and isinstance(max_price, int):
        db_records_by_price = ComputerComponentDatabase.records_in_range_by_price()
        records_by_price = db_records_by_price(key, min_price, max_price)

        if not save_request_history(message.chat.id, key, command, min_price, max_price, records_by_price):
            logger.warning(f'Ошибка при сохранении истории {message.chat.id}; {key}; {command}; {min_price}; '
                           f'{max_price}\n{records_by_price}')

    return output_records(bot, message, parameters, name, command, min_price, max_price,
                          start_index, max_index, records_by_price)


def save_request_history(user_id: int, key: str, command: str, min_price: int, max_price: int,
                         records_by_price) -> bool:
    """
    Функция сохраняет историю запросов в БД.

    :param: user_id - номер пользователя в чате.
    :type: str
    :param: key - выбранный компьютерный компонент.
    :type: str
    :param: command - выбранная команда.
    :type: str
    :param: min_price - минимальная цена компонента (левая граница диапазона цен).
    :type: int
    :param: max_price - максимальная цена компонента (правая граница диапазона цен).
    :type: int
    :param: records_by_price - записи по результатам запроса к базе данных
    :type: ModelSelect
    :return: True - успешное сохранение истории запросов в БД.
    False - сохранении истории запросов в БД завершилось ошибкой
    (неверно сформированы данные для сохранения).
    :rtype: bool
    """
    if len(records_by_price) > 0:
        history_list: List = list()
        history_list.append(deepcopy(history_table))
        history_list[0]['created_at'] = datetime.now()
        history_list[0]['user_id'] = user_id
        history_list[0]['command'] = command
        history_list[0]['computer_component'] = key
        history_list[0]['price_from'] = min_price
        history_list[0]['price_up_to'] = max_price
        history_list[0]['result'] = dict()

        result_list = load_model_in_json(records_by_price, 'title', 'link', 'price', 'img')
        for i_record, record in enumerate(result_list):
            history_list[0]['result'][i_record] = record

        db_load_history_table = ComputerComponentDatabase.load_history_table()
        if db_load_history_table(history_list):
            return True
        else:
            return False


def output_records_history(bot: TeleBot, message: Message, menu: Dict, parameters: Dict,
                           max_index: int, history_info: List[Dict]) -> None:
    """
    Функция выводит в чат прочитанные из БД записи истории запросов пользователя.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: menu - словарь наименований компьютерных компонентов для отображения.
    :type: Dict
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: max_index - максимальное количество одновременно выводимых элементов.
    :type: int
    :param: history_info - список словарей с информацией по истории запросов.
    :type: List[Dict]
    """
    key = parameters['key_button']
    records = [element for element in history_info[key]['result'].values()]
    data_model = load_data_in_model(computer_components[history_info[key]['computer_component']], records)
    output_records(bot, message, parameters,
                   menu[history_info[key]['computer_component']],
                   history_info[key]['command'], history_info[key]['price_from'],
                   history_info[key]['price_up_to'], parameters['start_index'],
                   max_index, data_model)


def read_and_output_history(bot: TeleBot, message: Message, menu_buttons: Dict, parameters: Dict,
                            max_index: int, history_info: List[Dict]) -> None:
    """
    Функция читает из БД историю запросов пользователя и выводит в чат.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: menu_buttons - словарь наименований компьютерных компонентов для отображения.
    :type: Dict
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: max_index - максимальное количество одновременно выводимых элементов.
    :type: int
    :param: history_info - список словарей с информацией по истории запросов.
    :type: List[Dict]
    """
    db_records_by_user_id = ComputerComponentDatabase.records_by_user_id()
    retrieved = db_records_by_user_id(message.chat.id)
    history_info.clear()
    records_count: int = len(retrieved)
    if records_count > 0:
        history_list = load_model_in_json(retrieved, 'created_at', 'user_id', 'command',
                                          'computer_component', 'price_from',
                                          'price_up_to', 'result')
        for element in history_list:
            history_info.append(element)
        menu: Dict = dict()
        start_index: int = parameters['start_index_button']
        end_index: int = start_index + max_index - 1
        for i_element, element in enumerate(history_info):
            if start_index <= i_element + 1 <= end_index:
                text = f"{menu_buttons[element['computer_component']]}: "
                if element['command'] == 'low':
                    text += f"мин. цена {element['price_from'] / 100}$ | "
                elif element['command'] == 'high':
                    text += f"макс. цена {element['price_from'] / 100}$ | "
                elif element['command'] == 'custom':
                    text += f"цена от {element['price_from'] / 100}$ до {element['price_up_to'] / 100}$ | "
                text += f"{element['created_at'].strftime('%d.%m.%Y %H:%M')}"
                menu[f"{i_element}"] = text
            elif i_element + 1 > end_index:
                break

        send_message_with_markup(bot, message, 'История запросов:', menu, number_columns=1,
                                 is_numbering=True, start_index=start_index)

        start_index = start_index + max_index
        end_index = start_index + max_index - 1
        if start_index <= records_count:
            if end_index > records_count:
                end_index = records_count
            menu_next_output = {'next_records_history': f'с {start_index} по {end_index} (всего {records_count})'}
            send_message_with_markup(bot, message, 'Следующие записи:', menu_next_output,
                                     number_columns=1, is_numbering=False)
            parameters['start_index_button'] = start_index
        else:
            parameters['start_index_button'] = 1

    else:
        send_message(bot, message, 'Запросов еще не было')


def price_range_request(bot: TeleBot, message: Message, name: str,
                        min_price: int, max_price: int) -> None:
    """
    Функция выводит в чат предложение задать диапазон цен для выполнения запроса.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: name - наименование компонента для отображения в чате.
    :type: str
    :param: min_price - минимальная цена компонента (левая граница диапазона цен).
    :type: int
    :param: max_price - максимальная цена компонента (правая граница диапазона цен).
    :type: int
    """
    if isinstance(min_price, int) and isinstance(max_price, int):
        text = f'{name}: минимальная цена {min_price / 100}$\n'
        text = ''.join((text, f'{name}: максимальная цена {max_price / 100}$\n'))
        send_message(bot, message, text)
        text = f'Введите диапазон цен (например: 100-150)'
        send_message(bot, message, text)
    else:
        send_message(bot, message, f'{name}\nЦены не заданы')


def price_range_read(bot: TeleBot, message: Message, parameters: Dict,
                     price_range: str, name: str, start_index: int, max_index: int) -> None:
    """
    Функция преобразует заданный пользователем диапазон цен в числовые значения.
    В случае успешного преобразования вызывается функция request_and_output_records_by_price.

    :param: bot - телеграм бот.
    :type: TeleBot
    :param: message - объект из telebot, содержащий информацию о сообщении.
    :type: Message
    :param: parameters - словарь с параметрами запроса.
    :type: Dict
    :param: price_range - ожидаемый диапазон цен от пользователя - текст из чата.
    :type: str
    :param: name - наименование компонента для отображения в чате.
    :type: str
    :param: start_index - начальный индекс элемента с которого начинается вывод результатов запроса.
    :type: int
    :param: max_index - максимальное количество одновременно выводимых элементов.
    :type: int
    """
    if parameters['command'] and parameters['computer_component'] and \
            parameters['min_price'] and parameters['max_price']:
        if parameters['command'] == 'custom':
            price_range = price_range.replace(' ', '')
            prices = price_range.split('-')
            text = 'Ошибка ввода диапазона цен. Попробуйте еще раз.'
            if len(prices) == 2:
                try:
                    parameters['price_from'] = int(prices[0]) * 100
                    parameters['price_up_to'] = int(prices[1]) * 100
                    if parameters['price_from'] <= parameters['price_up_to'] \
                            and (parameters['min_price'] <= parameters['price_from'] <= parameters['max_price']) \
                            and (parameters['min_price'] <= parameters['price_up_to'] <= parameters['max_price']):
                        request_and_output_records_by_price(bot, message, parameters,
                                                            parameters['computer_component'], name,
                                                            parameters['command'], parameters['price_from'],
                                                            parameters['price_up_to'], start_index, max_index)
                    else:
                        raise ValueError
                except ValueError:
                    send_message(bot, message, text)
                    logger.warning(f'Ошибка ввода диапазона цен: {price_range}; {name}\n{parameters}')
            else:
                send_message(bot, message, text)
                logger.warning(f'Ошибка ввода диапазона цен: {price_range}; {name}\n{parameters}')
