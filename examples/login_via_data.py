"""

    Пример #2. Авторизация с помощью личных данных пользователя.
    От прошлого отличается лишь тем, что тут указываются
    логин и пароль пользователя вместо токена.

    На выходе вы всегда можете получить Access-Token пользователя

    ATTENTION! Для данного вида авторизации требуется создать
    Standalone-приложение VK

    Создать можно тут -> https://vk.com/editapp?act=create
    От вас потребуется указать лишь ID вашего приложения, указанного
    в поле app_id

"""

# Импорт модуля
import vk_advanced_api

# Экземпляр класса VKAPI
api = vk_advanced_api.VKAPI(
    app_id='your-app-id',
    login='help@ar4ikov.ru',
    password='qwerty',
    captcha_key='your-captcha-key',
    version=5.71,
    warn_level=1,
    command_prefix='/'
)

# Utils - прямое взаимодействие с API VK
utils = api.utils

# Получаем информацию о пользователе, токен которого был указан
print(utils.users.get())