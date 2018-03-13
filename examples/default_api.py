"""

    Пример #5. Использование VK API напрямую.
    Действия всё те же. Но расскажу поподробнее об одном из них.


"""

# Импортируем модуль
import vk_advanced_api

# Создаем экземпляр класса VKAPI
api = vk_advanced_api.VKAPI(
    access_token='Your-Access-Token',
    captcha_key='your-captcha-key',
    version=5.71,
    warn_level=1
)

# Utils - прямое взаимодействие с API VK
utils = api.utils

# Utils по сути возвращает уже настроенный класс API
# Для обращения к этому классу используйте методы VK
#
# >>> utils.messages.send(user_id=1, message='Test')
#
# Мы вызываем метод messages.send с параметрами user_id=1 и message=Test
# При попытке указать заведомо неверный метод, класс вернет ошибку, которая
# уже взависимости от warn_level будет либо выведена на экран, либо вызвана, как ошибка.
#
# >>> utils.messsssages.sandWITHComg(usr_ed=1, messssssage='TOOOSTER')

# Верный метод
utils.messages.send(user_id=1, message='Test')

# Неверный метод
utils.messsssages.sandWITHComg(usr_ed=1, messssssage='TOOOSTER')