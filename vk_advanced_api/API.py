# ----------------------------
# | vk_advanced_api
# | Класс: API
# | Автор: https://vk.com/Ar4ikov
# | Создан 07.03.2018 - 8:19
# ----------------------------

import requests
from captcha_solver import CaptchaSolver
import re
import sys
from time import sleep

from vk_advanced_api.Request import Request
from vk_advanced_api import Pool as RequestPool
from uuid import uuid4 as UUID

class API_Constructor():
    def __init__(self, warn_level=None, api_source=None, access_token=None, session=requests.session(), proxy=None, rucaptcha_key=None, version=None):
        """

        Название класса довольно странное. Ведь оно
        символизирует не само тело запросов и обработку ошибок,
        а предназначено для определения отдельной структуры для аккаунта.

        :param api_source: - Ресурс API VK
        :param access_token: - Токен аккаунта VK
        :param version: - Версия API VK
        :param session: - Сессия для запросов (т.к. VK ввели привязку токена по IP, с которого был получен)
        :param proxy: - Прокси, с которого был получен токен
        :param rucaptcha_key: - RuCaptcha-Ключ для разгадки капч
        :param warn_level: - Уровень вывода ошибок и логов:
            > 1 - Выводит информацию в консоль
            > 2 - Выводит посредством вызова исключений (raise)
        """

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1'
        }
        self.access_token = access_token or None
        self.version = version or None
        self.session = session or None
        self.proxy = proxy or None
        self.rucaptcha_key = rucaptcha_key or None
        self.api_source = api_source or 'https://api.vk.com/method/'
        self.warn_level = warn_level or 1

    @staticmethod
    def getRequestingBody():
        return API_Constructor.getRequest

    def getRequest(self, method, **data):
        """

        Главный метод для запросов к API VK

        :param version: - Версия API VK
        :param session: - Текущая сессия сп ользователем
        :param method: - Необходимый метод
        :param proxy: - Прокси, с которого был получен токен
        :param data: - Собственно, все необходимые параметры
        :return: - Тело ответа, если не было ошибок
        """

        captcha_error = True
        captcha_key = None
        captcha_sid = None

        while captcha_error:
            # Добавляем к запросу параметры для разгадки капчи
            data['captcha_key'] = captcha_key
            data['captcha_sid'] = captcha_sid
            data['access_token'] = self.access_token
            data['v'] = self.version

            # Делаем запрос
            response = self.session.post(self.api_source + method, params=data, proxies={'https': self.proxy}, headers=self.headers)
            response_text = re.sub('true', 'True', response.text)
            response_text = re.sub('false', 'False', response_text)
            response_text = re.sub('null', 'None', response_text)

            # Проверяем на ошибки
            if eval(response_text).get('error'):

                error = eval(response.text)['error']
                if error['error_code'] == 14:
                    if self.rucaptcha_key:
                        captcha_img = eval(response.text)['error']['captcha_img']
                        captcha_img = re.sub(r'\\/', '/', captcha_img)
                        error['captcha_img'] = captcha_img

                        captcha_body = self.errorHandler(error=error)
                        captcha_sid = captcha_body['captcha_sid']
                        captcha_key = captcha_body['captcha_key']
                        print(captcha_key)
                elif error['error_code'] in [6, 900, 901, 902]:
                    self.errorHandler(error=error)
                else:
                    if self.warn_level == 1:
                        return error
                    elif self.warn_level == 2:
                        raise VKAPIError(error)
                    else:
                        raise VKAPITechnicalError('Неверный уровень логирования. Возможные уровни: 1, 2.')
            else:
                return eval(response_text)['response']

    def errorHandler(self, error):
        sender = self.getRequest(method='users.get')[0]['id']
        if error['error_code'] == 6:
            sleep(1)
            print("Запросы отправляются слишком быстро")
        elif error['error_code'] == 900:
            for item in error['request_params']:
                if item['key'] == 'user_id':
                    user_id = item['value']
                    print('Пользователь id{user_id} добавил аккаунт id{sender} в черный список'.format(user_id=user_id, sender=sender))
                    break
        elif error['error_code'] == 901:
            for item in error['request_params']:
                if item['key'] == 'user_id':
                    user_id = item['value']
                    print('Пользователь id{user_id} запретил отправку сообщений от имени сообщества'.format(user_id=user_id, sender=sender))
                    break
        elif error['error_code'] == 902:
            for item in error['request_params']:
                if item['key'] == 'user_id':
                    user_id = item['value']
                    print('Пользователь id{user_id} запретил отправлять ему сообщения в настройках приватности'.format(user_id=user_id))
                    break
        elif error['error_code'] == 14:
            print('Аккаунт id{} словил капчу! -> {}'.format(sender, error['captcha_img']))
            return {'captcha_key': self.getRuCaptchaSolver(self.savePhotoFrom(error['captcha_img'], 'captcha.png')), 'captcha_sid': error['captcha_sid']}

    def getRuCaptchaSolver(self, filename):
        """

        :param filename: - Имя файла с фотографией капчи
        :return: - Вернет саму отгадку капчи
        """

        while True:
            try:
                solver = CaptchaSolver('rucaptcha', api_key=self.rucaptcha_key)
                raw_data = open(filename, 'rb').read()

                return solver.solve_captcha(raw_data)

            except:
                pass

    def savePhotoFrom(self, server, filename):
        """
        Метод поможет сохранить фотографии прямо на оборудование

        :param server: - Сервер с фотографией
        :param filename: - Имя файла, куда нужно сохранить фотографию
        :return: - Вернет имя файла при удачном сохранении, или tuple(False, ошибка)
        """

        try:
            response = requests.get(server)
            out = open(filename, "wb")
            out.write(response.content)
            out.close()
            return filename

        except:
            return False, str(sys.exc_info())

class API_Object():
    def __init__(self, warn_level=None, method=None, api_source=None, access_token=None, proxy=None, rucaptcha_key=None, version=None):
        self.method = method or None
        self.access_token = access_token or None
        self.version = version or None
        self.proxy = proxy or None
        self.rucaptcha_key = rucaptcha_key or None
        self.api_source = api_source or None
        self.warn_level = warn_level or 1

    def __getattr__(self, method):
        return API_Object(
            method=self.method + "." + method,
            access_token=self.access_token,
            version=self.version,
            proxy=self.proxy,
            rucaptcha_key=self.rucaptcha_key,
            api_source=self.api_source,
            warn_level=self.warn_level or 1
        )

    def __call__(self, **kwargs):
        API = API_Constructor(
            access_token=self.access_token,
            version=self.version,
            proxy=self.proxy,
            rucaptcha_key=self.rucaptcha_key,
            api_source=self.api_source,
            warn_level=self.warn_level or 1
        )
        RequestPool.Pool.startPool()
        request = Request(method=self.method, cls=API, id=UUID(), **kwargs)

        RequestPool.Pool.addRequest(request)

        while True:
            for response in RequestPool.Pool.getProcessed():
                if response.getId() == request.getId():

                    RequestPool.Pool.processed.remove(response)
                    return response.body
class API():
    def __init__(self, warn_level=None, api_source=None, access_token=None, proxy=None, rucaptcha_key=None, version=None):
        self.access_token = access_token or None
        self.version = version or None
        self.proxy = proxy or None
        self.rucaptcha_key = rucaptcha_key or None
        self.api_source = api_source or None
        self.warn_level = warn_level or 1

    def __getattr__(self, method):
        return API_Object(
            method=method,
            access_token=self.access_token,
            version=self.version,
            proxy=self.proxy,
            rucaptcha_key=self.rucaptcha_key,
            api_source=self.api_source,
            warn_level = self.warn_level
        )

class VKAPIError(Exception):
    pass

class VKAPITechnicalError(Exception):
    pass