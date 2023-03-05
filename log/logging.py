from os import path, mkdir
from json import load
from logging import getLogger
from logging.config import dictConfig
from settings import SiteSettings

# Общие параметры
site = SiteSettings()
# Наименование папки с логом
folder_log: str = site.folder_log
# Наименование конфигурационного файла
logging_config_file: str = site.logging_config_file


class Logging:
    """
    Класс Logging - предоставляет методы и свойства для настройки логирования.

    Args:
    name (str): наименование объекта Logger
    template (str): наименование шаблона (по умолчанию 'default')
    file_name (str): наименование log файла (по умолчанию 'main.log')
    folder (str): наименование папки с лог файлом
    (по умолчанию folder_log - наименование папки, заданное в общих параметрах)
    config_file (str): наименование файла конфигурации логирования
    (по умолчанию logging_config_file - наименование файла конфигурации, заданное в общих параметрах)
    """
    def __init__(self, name: str, template: str = 'default', file_name: str = 'main.log',
                 folder: str = folder_log, config_file: str = logging_config_file) -> None:
        self._name = name
        self._template = template
        self._file_name = file_name
        self._folder = folder
        self._config_file = config_file

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        self._name = name

    @property
    def template(self) -> str:
        return self._template

    @template.setter
    def template(self, template: str) -> None:
        self._template = template

    @property
    def file_name(self) -> str:
        return self._file_name

    @file_name.setter
    def file_name(self, file_name: str) -> None:
        self._file_name = file_name

    @property
    def folder(self) -> str:
        return self._folder

    @folder.setter
    def folder(self, folder: str) -> None:
        self._folder = folder

    @property
    def config_file(self) -> str:
        return self._config_file

    @config_file.setter
    def config_file(self, config_file: str) -> None:
        self._config_file = config_file

    def create_log_folder(self) -> None:
        if not path.exists(self.folder):
            mkdir(self.folder)

    def get_logger(self):
        self.create_log_folder()
        with open(self.config_file, "r") as file:
            dict_config = load(file)
            self.file_name = path.join(self.folder, self.file_name)
            dict_config["handlers"]["rotating_file"]["filename"] = self.file_name
            dict_config["loggers"][self.name] = dict_config["loggers"][self.template]
        dictConfig(dict_config)
        return getLogger(self.name)

    def get_default_logger(self):
        self.create_log_folder()
        with open(self.config_file, "r") as file:
            dict_config = load(file)
            self.file_name = path.join(self.folder, self.file_name)
            dict_config["handlers"]["rotating_file"]["filename"] = self.file_name
            dictConfig(dict_config)
        return getLogger("default")
