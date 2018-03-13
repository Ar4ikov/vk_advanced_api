# VK Advanced API

Интересная штука то получается. Вроде всех этих open-source либ много, но все они
какие-то недоработанные.

Именно так я решил.
Решил и сделал

VK Advanced API предоставляет возможность в полной мере насладиться всеми
фичами API ВК, которое оно само предоставить не может.

Здесь вы увидите:
- Авторизация с помощью Логина и Пароля пользователя, а не только токена
- Улучшение работы некоторых методов и их группирование в один полноценно рабочий метод
- Улучшенный polling эвентов
- Обработку капчи с помощью сервиса RuCaptcha
- Кастомную обработку ошибок
- Качественную и быструю работу
- Гибкую настройку под все нужды

Это и не только вы сможете увидеть тут!

---
### Авторизация

(Все представленное здесь хорошо описано в директории examples)

Через данные пользователя
```python
# Импорт модуля
import vk_advanced_api

# Экземпляр класса VKAPI
api = vk_advanced_api.VKPAI(
    app_id='your-app-id',
    login='help@ar4ikov.ru',
    password='qwerty',
    captcha_key='your-captcha-key',
    version=5.71,
    warn_level=1
)
```
где:
- app_id - ID Вашего Standalone-приложения
- login - Логин/Email/Телефон юзера
- password - Пароль юзера
- captcha_key - API Ключ к вашему аккаунту на RuCaptcha
- version - Желаемая версия API VK
- warn_level - Уровень лога ошибок, где 1 - вывод в консоль, 2 - вызов ошибок (raise)

При данном типе авторизации будет получен Access Token юзера, так что вы всегда 
сможете получитьего
```python
access_token = api.access_token
```

Через токен
```python
# Импортируем модуль
import vk_advanced_api

# Создаем экземпляр класса VKAPI
api = vk_advanced_api.VKPAI(
    access_token='Your-Access-Token',
    captcha_key='your-captcha-key',
    version=5.71,
    warn_level=1
)
```
где:
- access_token - Access Token юзера

