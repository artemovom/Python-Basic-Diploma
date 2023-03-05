from typing import Dict, Any, Optional
from datetime import datetime
import peewee as pw
from playhouse.sqlite_ext import JSONField
from settings import SiteSettings

# Общие параметры
site = SiteSettings()

# База данных
db = pw.SqliteDatabase(site.db_path)


def dict_key_by_value(set_dict: Dict, set_value: Any) -> Optional[Any]:
    """
    Функция возвращает ключ словаря по значению.

    :param: set_dict - словарь.
    :type: Dict
    :param: set_value - заданное значение.
    :type: Any
    :return: result[0] - ключ словаря.
    :rtype: Optional[Any]
    """
    result = [key for key, value in set_dict.items() if set_value is value]
    return result[0]


class ModelBase(pw.Model):
    """
    Класс ModelBase - для создания моделей.
    Родитель: pw.Model

    """
    class Meta:
        database = db


class ModelBaseComputerComponents(ModelBase):
    """
    Класс ModelBaseComputerComponents - моделирует базовые параметры компьютерных компонентов.
    Родитель: ModelBase

    Attributes:
    id (pw.TextField): идентификатор компонента (ключевое поле)
    title (pw.TextField): наименование компонента
    link (pw.TextField): ссылка на компонент в интернет-магазине
    img (pw.TextField): ссылка на изображение компонента
    price (pw.IntegerField): стоимость компонента (по умолчанию 0)
    brand (pw.TextField): бренд компонента
    model (pw.TextField): модель компонента
    """
    id = pw.TextField(primary_key=True)
    title = pw.TextField()
    link = pw.TextField()
    img = pw.TextField()
    price = pw.IntegerField(default=0)
    brand = pw.TextField()
    model = pw.TextField()


class Update(ModelBase):
    """
    Класс Update - описывает таблицу обновлений компьютерных компонентов в базе данных.
    Родитель: ModelBase

    Attributes:
    computer_component (pw.TextField): наименование компьютерного компонента
    update_date (pw.DateField): дата следующего обновления
    """
    computer_component = pw.TextField()
    update_date = pw.DateField()


class History(ModelBase):
    """
    Класс History - описывает историю запросов компьютерных компонентов.
    Родитель: ModelBase

    Attributes:
    created_at (pw.DateField): дата, время запроса
    user_id (pw.IntegerField): ИД пользователя
    command (pw.TextField): команда
    computer_component (pw.TextField): наименование компьютерного компонента
    price_from (pw.IntegerField): стоимость компонента от (по умолчанию 0)
    price_up_to (pw.IntegerField): стоимость компонента до (по умолчанию 0)
    result (JSONField): результат выполнения запроса
    """
    created_at = pw.DateTimeField(default=datetime.now())
    user_id = pw.IntegerField()
    command = pw.TextField()
    computer_component = pw.TextField()
    price_from = pw.IntegerField(default=0)
    price_up_to = pw.IntegerField(default=0)
    result = JSONField()


class PowerSupply(ModelBaseComputerComponents):
    """
    Класс PowerSupply - моделирует параметры блока питания.
    Родитель: ModelBaseComputerComponents

    Attributes:
    power (pw.TextField): мощность блока питания
    color (pw.TextField): цвет блока питания
    efficiency (pw.TextField): коэффициент мощности блока питания
    """
    power = pw.TextField()
    color = pw.TextField()
    efficiency = pw.TextField()

    def __str__(self):
        return 'Блок питания'


class CaseFan(ModelBaseComputerComponents):
    """
    Класс PowerSupply - моделирует параметры вентилятора корпуса.
    Родитель: ModelBaseComputerComponents

    Attributes:
    rpm (pw.TextField): скорость вращения вентилятора
    airFlow (pw.TextField): воздушный поток вентилятора
    noiseLevel (pw.TextField): уровень шума вентилятора
    """
    rpm = pw.TextField()
    airFlow = pw.TextField()
    noiseLevel = pw.TextField()

    def __str__(self):
        return 'Вентилятор корпуса'


class Ram(ModelBaseComputerComponents):
    """
    Класс Ram - моделирует параметры оперативной памяти.
    Родитель: ModelBaseComputerComponents

    Attributes:
    size (pw.TextField): объем одной планки оперативной памяти
    quantity (pw.TextField): количество планок оперативной памяти
    type (pw.TextField): тип оперативной памяти
    """
    size = pw.TextField()
    quantity = pw.TextField()
    type = pw.TextField()

    def __str__(self):
        return 'Оперативная память'


class Mouse(ModelBaseComputerComponents):
    """
    Класс Mouse - моделирует параметры компьютерной мыши.
    Родитель: ModelBaseComputerComponents

    Attributes:
    trackingMethod (pw.TextField): тип сенсора мыши
    color (pw.TextField): цвет мыши
    wireless (pw.TextField): тип подключения мыши
    """
    trackingMethod = pw.TextField()
    color = pw.TextField()
    wireless = pw.TextField()

    def __str__(self):
        return 'Мышь'


class Keyboard(ModelBaseComputerComponents):
    """
    Класс Keyboard - моделирует параметры клавиатуры.
    Родитель: ModelBaseComputerComponents

    Attributes:
    style (pw.TextField): стиль клавиатуры
    backlit (pw.TextField): цвет клавиш клавиатуры
    color (pw.TextField): цвет клавиатуры
    wireless (pw.TextField): тип подключения клавиатуры
    """
    style = pw.TextField()
    backlit = pw.TextField()
    color = pw.TextField()
    wireless = pw.TextField()

    def __str__(self):
        return 'Клавиатура'


class CpuFan(ModelBaseComputerComponents):
    """
    Класс CpuFan - моделирует параметры вентилятора процессора.
    Родитель: ModelBaseComputerComponents

    Attributes:
    rpm (pw.TextField): скорость вращения вентилятора
    color (pw.TextField): цвет вентилятора
    noiseLevel (pw.TextField): уровень шума вентилятора
    """
    rpm = pw.TextField()
    color = pw.TextField()
    noiseLevel = pw.TextField()

    def __str__(self):
        return 'Вентилятор процессора'


class Case(ModelBaseComputerComponents):
    """
    Класс Case - моделирует параметры корпуса.
    Родитель: ModelBaseComputerComponents

    Attributes:
    sidePanel (pw.TextField): боковая панель корпуса
    color (pw.TextField): цвет корпуса
    cabinetType (pw.TextField): тип корпуса
    """
    sidePanel = pw.TextField()
    color = pw.TextField()
    cabinetType = pw.TextField()

    def __str__(self):
        return 'Корпус'


class Storage(ModelBaseComputerComponents):
    """
    Класс Storage - моделирует параметры хранилища.
    Родитель: ModelBaseComputerComponents

    Attributes:
    storageInterface (pw.TextField): интерфейс хранилища
    rpm (pw.TextField): скорость вращения
    type (pw.TextField): тип хранилища
    cacheMemory (pw.TextField): кэш-память
    """
    storageInterface = pw.TextField()
    rpm = pw.TextField()
    type = pw.TextField()
    cacheMemory = pw.TextField()

    def __str__(self):
        return 'Внешняя память'


class Processor(ModelBaseComputerComponents):
    """
    Класс Processor - моделирует параметры процессора.
    Родитель: ModelBaseComputerComponents

    Attributes:
    speed (pw.TextField): скорость процессора
    socketType (pw.TextField): разъем процессора
    """
    speed = pw.TextField()
    socketType = pw.TextField()

    def __str__(self):
        return 'Процессор'


class Gpu(ModelBaseComputerComponents):
    """
    Класс Gpu - графическая карта.
    Родитель: ModelBaseComputerComponents

    Attributes:
    storageInterface (pw.TextField): интерфейс
    memory (pw.TextField): память
    clockSpeed (pw.TextField): тактовая частота графического процессора
    chipset (pw.TextField): чипсет
    """
    storageInterface = pw.TextField()
    memory = pw.TextField()
    clockSpeed = pw.TextField()
    chipset = pw.TextField()

    def __str__(self):
        return 'Видеокарта'


class Motherboard(ModelBaseComputerComponents):
    """
    Класс Motherboard - материнская плата.
    Родитель: ModelBaseComputerComponents

    Attributes:
    formFactor (pw.TextField): форм-фактор материнской платы
    chipset (pw.TextField): чипсет материнской платы
    memorySlots (pw.TextField): слоты памяти материнской платы
    socketType (pw.TextField): тип разъема материнской платы
    """
    formFactor = pw.TextField()
    chipset = pw.TextField()
    memorySlots = pw.TextField()
    socketType = pw.TextField()

    def __str__(self):
        return 'Материнская плата'
