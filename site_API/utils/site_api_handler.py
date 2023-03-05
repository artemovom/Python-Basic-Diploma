from requests import request, Response
from typing import Dict, Union, Callable


def _make_response(method: str, url: str, headers: Dict, params: Dict,
                   timeout: int, success: int = 200) -> Union[Response, int]:
    """
    Функция отправляющая HTTP запросы с помощью библиотеки request.

    :param: method - тип HTTP запроса (GET, POST и др.).
    :type: str
    :param: url - URL запроса.
    :type: str
    :param: headers - HTTP заголовок запроса.
    :type: Dict
    :param: params - параметры запроса.
    :type: Dict
    :param: timeout - время ожидания ответа.
    :type: int
    :param: success - код статуса запроса (по умолчанию 200).
    :type: int
    :return: response, status_code - в случае успешного запроса (status_code = 200),
    возвращается результат запроса, в противном случае возвращается код ответа.
    :rtype: Union[Response, int]
    """
    response = request(method, url, headers=headers, params=params, timeout=timeout)
    status_code = response.status_code

    if status_code == success:
        return response

    return status_code


def _get_endpoint(method: str, url: str, headers: Dict, params: Dict, computer_component: str,
                  timeout: int, func: Callable = _make_response) -> Response:
    """
    Функция получения endpoint с сайта API.

    :param: method - тип HTTP запроса (GET, POST и др.).
    :type: str
    :param: url - URL запроса.
    :type: str
    :param: headers - HTTP заголовок запроса.
    :type: Dict
    :param: params - параметры запроса.
    :type: Dict
    :param: computer_component - наименование компьютерного компонента.
    :type: str
    :param: timeout - время ожидания ответа.
    :type: int
    :param: func - вызываемая функция, отправляющая HTTP запросы.
    :type: Callable
    :return: response - результат выполнения запроса
    :rtype: Response
    """
    url = '{0}/{1}'.format(url, computer_component)
    response = func(method, url, headers=headers, params=params, timeout=timeout)

    return response


class SiteApiInterface:
    """
    Класс SiteApiInterface - предоставляет методы для получения данных с сайта API.

    """
    @staticmethod
    def get_endpoint():
        return _get_endpoint


if __name__ == "__main__":
    SiteApiInterface()
