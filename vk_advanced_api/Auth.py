# ---------------------------
# | vk_advanced_api
# | Класс: Auth
# | Автор: https://vk.com/Ar4ikov
# | Создан 12.03.2018 - 18:56
# ---------------------------

from parsel import Selector
import requests
import lxml.html

class Auth():
    def __init__(self, access_token=None, login=None, password=None, proxy=None, app_id=None, scopes_list=None, version=None):
        """

        Класс аунтификации юзера через кастомное Standalone-приложение VK

        :param access_token: - Access-Token юзера, если есть, класс становиться бесполезен o_0
        :param login: - Логин/Email/Телефон пользователя
        :param password: - Пароль пользователя
        :param proxy: - Прокси, с которого нужно получить токен, в данном случае, не используется
        :param app_id: - APP_ID Standalone-приложения VK
        :param scopes_list: - Список прав доступа токена
        :param version: - Версия API VK
        """

        self.access_token = None
        self.proxy = proxy or None
        self.app_id = app_id or None
        self.version = version or None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'DNT': '1'
        }
        if not access_token:
            self.login = login or None
            self.password = password or None
            self.access_token = self.getToken(scopes_list=scopes_list)
        else:
            self.access_token = access_token or None

    def pasre(self, response, tag):
        responseTags = []
        for tags in Selector(response).css(tag).extract():
            responseTags.append(tags)

        response = []
        for tags in responseTags:
            response.append({
                'grant-access': Selector(tags).css('form::attr(action)').extract_first(),
            })

        return response

    def doLogin(self):
        """

        Позволяет выполнить вход в аккаунт VK

        :return: - Сессию, которая потребуется для получения токена
        """
        if self.access_token:
            return self.access_token

        request = 'https://vk.com'
        session = requests.Session()
        data = session.post(request, headers=self.headers, proxies={'https': self.proxy})
        page = lxml.html.fromstring(data.content)

        form = page.forms[0]
        form.fields['email'] = self.login
        form.fields['pass'] = self.password

        response = session.post(form.action, data=form.form_values(), proxies={'https': self.proxy})
        if 'onLoginDone' in response.text:
            self.session = session
            return session
        else:
            raise VKAuthError("Не удалось авторизироваться: неправильный логин или пароль.\n"
                              "Тажке это может быть связано с двухфакторной аунтификацией.\n"
                              "Попробуйте отключить её в настройках безопасности и повторить попытку снова.")

    def getToken(self, scopes_list=None):
        """

        Метод по получению токена с сессии пользователя

        :param session: - Сессия, с которой был выполнен вход в аккаунт
        :param scopes_list: - Список прав, которые следует получить
        :return: Токен для работы с API VK
        """
        self.session = self.doLogin()

        if self.access_token:
            return self.access_token

        # Полный легальный список возможных методов
        scopes_list = scopes_list or [
            'audio',
            'notify',
            'friends',
            'photos',
            'video',
            'stories',
            'pages',
            'status',
            'notes',
            'messages',
            'wall',
            'ads',
            'offline',
            'docs',
            'groups',
            'notifications',
            'stats',
            'email',
            'market'
                                    ]
        scopes = ""
        app_id = self.app_id

        i = 0
        for scope in scopes_list:
            if i == len(scopes_list)-1:
                scopes = scopes + scope
            else:
                scopes = scopes + scope + "%2C"
            i += 1

        # Далее - костыльный и некрасивый код :(
        # Он не достоин вашего внимания!

        request = 'https://oauth.vk.com/authorize?client_id={app_id}&scope={scopes}&redirect_uri=https://oauth.vk.com/blank.html&display=page&v=5.69&response_type=token'.format(app_id=app_id, scopes=scopes)

        response = self.session.post(request, proxies={'https': self.proxy})

        try:
            body = eval(response.text)
            if body.get('error'):
                raise VKAuthError(body)
        except VKAuthError:
            body = eval(response.text)
            raise VKAuthError(body)
        except:
            pass

        if not response.url.count('authorize'):
            token = response.url[45:130]
            return token

        response = response.text

        try:
            body = eval(response)
            if body.get('error'):
                raise VKAuthError(body)
        except VKAuthError:
            body = eval(response)
            raise VKAuthError(body)
        except:
            pass

        link = self.pasre(response=response, tag='form')[0]['grant-access']
        token =  self.session.post(link, proxies={'https': self.proxy}).url[45:130]
        return token

class VKAuthError(Exception):
    pass
