## Описание телеграм-бота

Телеграм-бот предоставляет информацию по компьютерным компонентам:
- Корпус
- Вентилятор корпуса
- Вентилятор процессора
- Видеокарта
- Клавиатура
- Материнская плата
- Мышь
- Блок питания
- Процессор
- Оперативная память
- Внешняя память

Телеграм-бот: [@ComputerComponentsBot](https://t.me/ComputerComponentsBot)

Телеграм-бот работает с RapidAPI (https://rapidapi.com/idirmosh/api/computer-components-api).

## Запуск телеграмм бота

Запустить файл main.py в корне проекта

Для начала работы ввести одну из следующих команд:
- Привет
- /start
- /help

## Команды телеграм бота
- /start - выводит приглашение и меню с командами боту.
- /help (или Справка) - выводит подсказку по командам бота.
- /low - выводит минимальные показатели (с изображением товара).
- /high - выводит максимальные показатели (с изображением товара).
- /custom - выводит показатели пользовательского диапазона (с изображением товара).
- /history (или История) - выводит историю запросов пользователя.
- /stop (или Завершить) - закрывает меню с командами.

## Описание модулей
- database - работает с базой данных.
- log - работает с лог-файлами.
- site_API - работает с API стороннего сайта
- tg_API - основной модуль, работает с Telegram
- .env - параметры проекта
- сс.db - база данных
- main.py - запуск телеграм бота
- requirements.txt - требования
- settings.py - чтение параметров проекта

## База данных
База данных sqlite3, версия 2.0.4.
База данных реализована с использованием peewee.

В базе данных хранится:
- Информация о компьютерных компонентах, загруженная с RapidAPI.
- Информация о дате последнего обновления по каждому компьютерному компоненту
- История запросов пользователя

Процесс обновления компьютерных компонент реализован в функции database_loading (tg_API/core.py).
При старте телеграм-бота функция database_loading запускается в отдельном процессе.
Функция периодически (1 раз в сутки) производит проверку таблицы Update 
и обновляет информацию о компьютерных компонентах с сайта rapidAPI.
