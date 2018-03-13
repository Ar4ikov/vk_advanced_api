# ---------------------------
# | vk_advanced_api
# | Класс: VKAPI
# | Автор: https://vk.com/Ar4ikov
# | Версия: 1.0.0
# | Создан 07.03.2018 - 9:29
# ---------------------------

__version__ = '1.0.0'

import re
import time
from threading import Thread
from time import sleep

import pymitter
import requests

from vk_advanced_api import API
from vk_advanced_api.Auth import Auth


class VKAPI():
    def __init__(self, access_token=None, login=None, password=None, app_id=None, version=None, captcha_key=None, warn_level=None):
        """

        VK Advanced API - Продвинутое OpenSource API на Python для VK

        :param access_token: - Access Token пользователя
        :param login: - Логин/Email/Телефон пользователя VK
        :param password: - Пароль пользователя VK
        :param app_id: - APP_ID Standalone-приложения VK
        :param version: - Версия API VK
        :param captcha_key: - RuСaptcha API ключ
        :param warn_level: - Уровень вывода ошибок и логов:
            > 1 - Выводит информацию в консоль
            > 2 - Выводит посредством вызова исключений (raise)
        """
        self.version = version or 5.71

        self.warn_level = warn_level or 1

        self.poll = pymitter.EventEmitter()

        if not access_token:
            self.login = login or None
            self.password = password or None
            self.app_id = app_id or None
            self.Auth = Auth(login=self.login, password=self.password, app_id=self.app_id, version=self.version)
            self.access_token = self.Auth.access_token
        else:
            self.access_token = access_token or None

        self.api = API.API(
            warn_level=self.warn_level,
            access_token=self.access_token,
            version=self.version,
            rucaptcha_key=captcha_key or None,
            proxy=None
            )

        self.bot_id = self.api.users.get()[0]['id']
        sleep(0.34)

        self.start_time = str(int(time.time()))[0:10]

    @property
    def utils(self):
        """

        Получаем прямой доступ к библиотеке методов

        :return:
        """
        return self.api

    def sendMessage(self, user_id, message, attachments=[]):
        """

        Улучшенная функция отправки сообщения

        :param user_id: - peer_id чата/беседы или user_id пользователя VK
        :param message: - Сообщение, которое необходимо отправить
        :param attachments: - Прикрепленные файлы, данные от которых можно получить
        из методов ниже
        :return: - None
        """
        attach = ""
        for file in attachments:
            attach = attach + file + ","

        try:
            self.api.messages.send(peer_id=user_id, message=message, attachment=attach)
        except Exception as error:
            self.poll.emit('error', {'body': str(error)})
        sleep(0.34)

    def getPollingDetails(self):
        """

        Позволяет получить данные от Polling-сервера VK
        :return: - Вернет JSON-схему с содежимым server, key, ts
        """
        sleep(0.34)
        polling_details = self.api.messages.getLongPollServer()
        server, key, ts = polling_details['server'], polling_details['key'], polling_details['ts']
        return {'server': server, 'key': key, 'ts': ts}

    def __str__(self):
        return str({'access_token': self.access_token, 'started_at': self.start_time})

    def isOut(self, flags):
        """

        Позволяет определить, является ли сообшение исходящим

        :param flags: - Флаг нужного сообщения
        :return: Вернет True, если сообщение исходящее
        """
        HIDDEN = flags // 65536
        HIDDEN_mod = flags % 65536
        MEDIA = HIDDEN_mod // 512
        MEDIA_mod = HIDDEN_mod % 512
        FIXED = MEDIA_mod // 256
        FIXED_mod = MEDIA_mod % 256
        DELЕTЕD = FIXED_mod // 128
        DELЕTЕD_mod = FIXED_mod % 128
        SPAM = DELЕTЕD_mod // 64
        SPAM_mod = DELЕTЕD_mod % 64
        FRIENDS = SPAM_mod // 32
        FRIENDS_mod = SPAM_mod % 32
        CHAT = FRIENDS_mod // 16
        CHAT_mod = FRIENDS_mod % 16
        IMPORTANT = CHAT_mod // 8
        IMPORTANT_mod = CHAT_mod % 8
        REPLIED = IMPORTANT_mod // 4
        REPLIED_mod = IMPORTANT_mod % 4
        OUTBOX = REPLIED_mod // 2
        OUTBOX_mod = REPLIED_mod % 2
        UNREAD = OUTBOX_mod // 1
        if OUTBOX > 0:
            return True
        else:
            return False

    def updatingDetails(self):
        """

        Обновляет каждые 10 минут данные для подключения к Polling-серверу

        :return: - Обновляет self.details
        """
        while True:
            sleep(600)
            try:
                self.details = self.getPollingDetails()
            except Exception as error:
                self.poll.emit('error', {'body': str(error)})

    def pollingRequesting(self):
        """

        Отправка запросов на Polling-сервера VK
        Чтобы получить их, используется метод messages.getLongPollingServer

        :return: - Добавляет новый эвент в self.events
        """
        self.events = []
        self.details = self.getPollingDetails()
        while True:
            try:
                self.details['server'] = re.sub(r'\\/', '/', self.details['server'])
                response = eval(requests.get('https://{}'.format(self.details['server']),
                                         params={'act': 'a_check', 'key': self.details['key'], 'ts': self.details['ts'],
                                                 'wait': 0, 'version': 2, 'mode': 2}).text)
                self.events = response['updates']
            except Exception as error:
                self.poll.emit('error', {'body': str(error)})

    def pollingHandler(self):
        """

        Обработка ответов с Polling-сервера
        Различаются 3 типа эвентов (два с утвердительным ответом и один с ошибочным)

        :event new_message: - Новое сообщения в беседе, личных сообщениях (от групп или от человека)
        :event new_action: - Эвент, который возможен только в чатах/беседах

        :return: - None
        """
        while True:
            messages = []
            for event in self.events:
                if event[0] == 4:
                    messages.append(event)

            new_events = []
            for event in messages:
                from_id = None
                if event[-1].get('from'):
                    msg_type = 'public'
                    from_id = event[-1].get('from')
                else:
                    msg_type = 'private'

                if event[-1].get('source_act'):
                    isActed = True
                else:
                    isActed = False

                act = event[-1].get('source_act')
                act_mid = event[-1].get('source_mid')
                act_text = event[-1].get('source_text')
                act_from = event[-1].get('from')

                attachments = []
                attach_key = 'attach1'
                attach_type = 'attach1_type'
                for i in range(1,11):
                    if event[-1].get(attach_key):
                        attachments.append(attach_type + "_" + attach_key)
                        attach_key = attach_key[0:6] + str(i+1)
                        attach_type = attach_key + "_type"
                    else:
                        break

                args = re.sub(r'\\/', '/', event[5])
                args = args.split(' ')

                isCommand = None
                isOut = None
                if len(''.join(args)) > 0:
                    if args[0][0] == '/':
                        isCommand = True
                    else:
                        isCommand = False

                if self.isOut(event[2]):
                    isOut = True
                else:
                    isOut = False

                if isActed == False:
                    new_events.append(
                            dict(event='new_message', type=msg_type, is_out=isOut, args=args, is_command=isCommand, peer_id=event[3],
                                 from_id=from_id, body=event, is_acted=isActed, attachments=attachments))
                else:
                    new_events.append(dict(event='new_action', attachments=attachments, peer_id=event[3], type=msg_type, is_out=isOut, from_id=from_id, is_acted=isActed,
                                               acts=dict(act=act, act_mid=act_mid, act_text=act_text,
                                                         act_from=act_from)))

            for new in new_events:
                if new['event'] == 'new_action':
                    self.poll.emit('new_action', new)
                elif new['event'] == 'new_message':
                    if new['is_command'] == True:
                        self.poll.emit('new_message', new, command=new['args'][0])
                    else:
                        self.poll.emit('new_message', new, command=None)

            self.details = self.getPollingDetails()

    def polling(self):
        """

        Технология Polling (LongPolling) -  универсальное средство получения ответа тогда, когда он поступит
        Значительно сокращает количество запросов на сервер, благодаря тому что сервер
        отошлет ответ только тогда, когда появится новый эвент. В противном случае вернет пустой
        ответ через указанное время ожидание.

        VK и многие другие сервисы имеют в своих API эту возможность
        Подробнее -> https://vk.com/dev/using_longpoll

        :return: - None
        """

        tasks = [
            self.pollingRequesting,
            self.pollingHandler,
            self.updatingDetails
                 ]
        for task in tasks:
            print('Создаю поток для {}'.format(task))
            thread = Thread(target=task, args=())
            thread.start()

    def sendAudio(self, files):
        """

        Отправка аудио, как голосовые сообщения в личные сообщения

        :param files: - Список, с именем файлов, которые нужно загрузить и отправить
        :return: - Вернет список с JSON-схемами, хранящие информацию о загруженных аудиозаписей
        """
        getUploadServer = self.api.docs.getUploadServer(type="audio_message")
        upload_url = getUploadServer["upload_url"]
        result = []
        for file in files:
            try:
                up_res = requests.post(upload_url, files={'file': open(file, "rb")})
                up_res = eval(up_res.text)
                sleep(0.34)
                getVKFile = self.api.docs.save(file=up_res["file"], title="SuperCraft", tags="SuperCraft Audios")
                getVKFile = "audio" + str(getVKFile['owner_id']) + "_" + str(getVKFile['id'])
                result.append(getVKFile)
            except Exception as error:
                self.poll.emit('error', {'body': str(error)})
        return result

    def sendVideo(self, files):
        """

        Отправка видео в личные сообщения

        :param files: - Список, с именем файлов, которые нужно загрузить и отправить
        :return: - Вернет список с JSON-схемами, хранящие информацию о загруженных видеороликах
        """
        getUploadServer = self.api.video.save(name='SuperCraft', description='SuperCraft', is_private=False)
        upload_url = getUploadServer["upload_url"]
        result = []
        for file in files:
            try:
                up_res = requests.post(upload_url, files={'file': open(file, "rb")})
                up_res = eval(up_res.text)
                sleep(0.34)
                getVKFile = 'video' + str(self.bot_id) + "_" + str(up_res['video_id'])
                #getVKFile = self.api.photos.saveMessagesPhoto(photo=up_res["photo"], server=up_res["server"], hash=up_res["hash"])
                result.append(getVKFile)
            except Exception as error:
                self.poll.emit('error', {'body': str(error)})
        return result

    def sendPhoto(self, files):
        """

        Отправка фотографий на сервер в сообщения

        :param files: - Список, с именем файлов, которые нужно загрузить и отправить
        :return: - Вернет список с JSON-схемами, хранящие информацию о загруженных фотографиях
        """
        getUploadServer = self.api.photos.getMessagesUploadServer()
        upload_url = getUploadServer["upload_url"]
        result = []
        i = 0
        for file in files:
            try:
                up_res = requests.post(upload_url, files={'file': open(file, "rb")})
                up_res = eval(up_res.text)
                sleep(0.34)
                getVKFile = self.api.photos.saveMessagesPhoto(photo=up_res["photo"], server=up_res["server"], hash=up_res["hash"])
                getVKFile = "photo" + str(getVKFile[i]['owner_id']) + "_" + str(getVKFile[i]['id'])
                result.append(getVKFile)
                i +=1
            except Exception as error:
                self.poll.emit('error', {'body': str(error)})
        return result