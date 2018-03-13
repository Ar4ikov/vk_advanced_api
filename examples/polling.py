"""

    Пример #3. Работа с эвентами или LongPolling-сервером.
    Подробнее о LongPolling VK -> https://vk.com/dev/using_longpoll

    Наше API подразумивает собой обработку многих эвентов.
    Но пока доступны (и сделаны xD) только 2.

    - new_message - Новое сообщение в беседе или личных сообщениях
        > type - тип сообщения:
            - public - если сообщение из беседы
            - private - если сообщение носит личный характер
        > is_out - Определяет, явзяется ли сообщение исходящим (True, если да)
        > args - Аргументы (просто всё, что разделено пробелом), помогают при создании команд для чат-бота
        > is_command - Определяет, является ли сообщение командой (True, если да)
        > peer_id - ID диалога (диалогом может быть беседа или личный чат)
        > from_id - (только для бесед, вернет None, если личное сообщение) - ID пользователя, который отправил сообщение
        > body - Тело эвента в нетронутом виде, которое поступило при запросе на Polling сервер VK
        > is_acted (только для бесед, вернет False, если личное сообщение) - Позволяет определить, является ли этот эвент действием в беседе (True, если является)
        > attachments - Вложения вида:
        [
            owner_id + "_" + id
        ]

    - new_action - Эвент, привязанный к беседе, позволяет узнать, кто кого кикнул или пригласил,
                    кто сменил фотографию или название беседы
        > attachments - вложения вида:
        [
            owner_id + "_" + id
        ]
        > peer_id - ID диалога (диалогом может быть беседа или личный чат)
        > type - тип сообщения:
            - public - если сообщение из беседы
            - private - если сообщение носит личный характер
        > from_id - (только для бесед, вернет None, если личное сообщение) - ID пользователя, который отправил сообщение
        > is_acted (только для бесед, вернет False, если личное сообщение) - Позволяет определить, является ли этот эвент действием в беседе (True, если является)
        > is_out - Определяет, явзяется ли сообщение исходящим (True, если да)
        > acts - Сами действия, которые произошли в беседе. Вид:
        {
            > act - id действия
            > act_mid - ID юзера, над которым совершили действие
            > act_from - ID юзера, который совершил действие
            > act_text - Текст, который был передан в действии (обычно новое название беседы)
        }

    - error - Технический эвент, позволяет обработать ошибки класса VKAPI
    Ошибки класса API (или utils) обрабатываются внутри класса

    Больше эвентов в обновлениях!

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

# Включаем Polling
api.polling()

# Прослушиваем эвент new_messages
@api.poll.on('new_message')
def bot(event, command):
    """

    Функция, которая выполняется при прослушивании эвента

    :param event: - Тело эвента
    :param command: - Команда, которую указал пользователь (если сообщение
                    носит обычный характер, вернет None)
    :return: - None или True или False
    """
    print("Новое сообщение -> {}".format(event))
    if command:
        print('Требуется выполнить команду -> {}'.format(command))

        # Определяем, что за команда была указана
        if command == '/about':
            api.sendMessage(user_id=event['peer_id'], message='Я - новый бот VK!\nЯ использую новую open-source библиотеку vk_advanced_api (https://github.com/Ar4ikov/vk_advanced_api)')

@api.poll.on('new_action')
def onAction(event):
    """

    Функция обработки актов в беседах

    :param event: - Тело эвента
    :return: - None или True или False
    """

    # Тело события
    print("Новое событие в беседе -> {}".format(event))

    # Определяем само событие и обрабатываем его
    # Более подробно -> https://vk.com/dev/using_longpoll_2 (6. Вложения и дополнительные данные)
    if event['acts']['act'] == 'chat_create':
        print('Создан чат с названием {}'.format(event['acts']['act_text']))

    elif event['acts']['act'] == 'chat_title_update':
        print('{user} сменил название чата на {title}'.format(user=event['acts']['act_from'], title=event['acts']['act_text']))

    elif event['acts']['act'] == 'chat_photo_update':
        print('{} сменил фотографию чата'.format(event['acts']['act_from']))

    elif event['acts']['act'] == 'chat_invite_user':
        print('{user} пригласил в чат {mid}'.format(user=event['acts']['act_from'], mid=event['acts']['act_mid']))

    elif event['acts']['act'] == 'chat_kick_user':
        print('{user} кикнул из чата {mid}'.format(user=event['acts']['act_from'], mid=event['acts']['act_mid']))

@api.poll.on('error')
def errorHandler(event):
    """

    Обработка ошибок класса VKAPI

    :param event: - Тело ошибки
    :return:
    """
    print('Новая ошибка -> {}'.format(event))