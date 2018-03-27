"""

    Пример #6. Работа с флагами эвента.
    Стало возможным после добавления в патче 1.1.0 метода `getFlags`

"""

# Импортируем модуль
import vk_advanced_api

# Создаем экземпляр класса VKAPI
api = vk_advanced_api.VKAPI(
    access_token='Your-Access-Token',
    captcha_key='your-captcha-key',
    version=5.71,
    warn_level=1,
    command_prefix='/'
)

api.polling()

@api.poll.on('new_message')
def new_message(event, command):
    """

    Получим флаги сообщения и переведем их в человеческий вид

    :param event:
    :param command:
    :return:
    """

    # Обрабится к оригинальному эвенту и получим третий элемент списка с флагами
    flags = event['body'][2]

    # Вызовем метод `getFlags`, который принимает INTEGER-значение ID флагов из эвента
    # Вернет список с названиями флагов. Более подробно на https://vk.com/dev/using_longpoll_2
    flags = api.getFlags(flags)

    print('Флаги сообщения с ID {id} -> {flags}'.format(id=event['message_id'], flags=flags))
