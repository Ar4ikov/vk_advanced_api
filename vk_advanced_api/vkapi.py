# ---------------------------
# | vk_advanced_api
# | Класс: VKAPI
# | Автор: https://vk.com/Ar4ikov
# | Создан 07.03.2018 - 9:29
# ---------------------------
import os

with open(os.path.join(os.path.dirname(__file__), 'version')) as f:
    __version__ = f.readline().strip()

import re
import time
from threading import Thread
from time import sleep

import pymitter
import requests

from vk_advanced_api import API
from vk_advanced_api.Auth import Auth


class VKAPI():
    def __init__(self, access_token=None, login=None, password=None, app_id=None, version=None, captcha_key=None, warn_level=None, command_prefix='/'):
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
        :param command_prefix: - Префикс для объявления команд (на них будет реагиорвать API)
        """
        self.version = version or 5.73
        self.command_prefix = command_prefix or '/'

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

        # Запрос на проверку типа токена:
        # - User Access Token
        # - Group Access Token

        self.token_type = None

        self.bot_fields = self.api.users.get()
        if len(self.bot_fields) > 0:
            self.token_type = 'user'
            self.bot_id = self.bot_fields[0]['id']
        else:
            self.token_type = 'group'
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
        if self.token_type == 'user':
            polling_details = self.api.messages.getLongPollServer()
        else:
            polling_details = self.api.groups.getLongPollServer()

        # Какова приичина такого выбора через цикл?
        # Ошибки были при самом запросе, которые возникали вот просто из ни откуда.
        # Пришлось сделать такую конструкцию. В любом случае, больше двух ошибок быть не может, ведь так?(
        while True:
            try:
                server, key, ts = polling_details['server'], polling_details['key'], polling_details['ts']
                return {'server': server, 'key': key, 'ts': ts}
            except:
                sleep(0.34)
                polling_details = self.api.messages.getLongPollServer()

    def __str__(self):
        return str({'access_token': self.access_token, 'started_at': self.start_time})

    def getFlags(self, flags):
        """

        Разбирает ID флагов на строковые параметры

        :param flags: - ID флагов нужного сообщения
        :return: - Вернет все ненулевые флаги
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

        response = []

        if HIDDEN > 0: response.append('HIDDEN')
        if MEDIA > 0: response.append('MEDIA')
        if FIXED > 0: response.append('FIXED')
        if DELЕTЕD > 0: response.append('DELETED')
        if SPAM > 0: response.append('SPAM')
        if FRIENDS > 0: response.append('FRIENDS')
        if CHAT > 0: response.append('CHAT')
        if IMPORTANT > 0: response.append('IMPORTANT')
        if REPLIED > 0: response.append('REPLIED')
        if OUTBOX > 0: response.append('OUTBOX')
        if UNREAD > 0: response.append('UNREAD')

        return response

    def isOut(self, flags):
        if self.getFlags(flags).count('OUTBOX'):
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

    def PollingRequesting(self):
        """

        Первая часть ->
        Отправка запросов на Polling-сервера VK
        Чтобы получить их, используется метод messages.getLongPollingServer

        Вторая часть ->
        Обработка ответов с Polling-сервера
        Различаются 3 типа эвентов (два с утвердительным ответом и один с ошибочным)
        :event new_message: - Новое сообщения в беседе, личных сообщениях (от групп или от человека)

        :event new_action: - Эвент, который возможен только в чатах/беседах

        :return: - Добавляет новый эвент в self.events
        """

        # Часть 1 ->
        global response
        self.events = []
        self.details = self.getPollingDetails()
        while True:
            try:
                self.details['server'] = re.sub(r'\\/', '/', self.details['server'])
                response = eval(requests.get('https://{}'.format(self.details['server']),
                                         params={
                                             'act': 'a_check',
                                             'key': self.details['key'],
                                             'ts': self.details['ts'],
                                             'wait': 25,
                                             'version': 2,
                                             'mode': 2
                                         }).text)
                self.events = response['updates']
                self.details['ts'] = response['ts']
            except Exception as error:
                self.poll.emit('error', {'body': str(error) + " -> " + response})
            else:
                # Часть два ->
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
                            attachments.append(event[-1].get(attach_type) + event[-1].get(attach_key))
                            attach_key = attach_key[0:6] + str(i+1)
                            attach_type = attach_key + "_type"
                        else:
                            break

                    args = re.sub(r'\\/', '/', event[5])
                    args = args.split(' ')

                    isCommand = None
                    isOut = None
                    if len(''.join(args)) > 0:
                        if len(args) > 0:
                            if len(args[0]) > 0:
                                if args[0][0] == self.command_prefix:
                                    isCommand = True
                                else:
                                    isCommand = False

                    if self.isOut(event[2]):
                        isOut = True
                    else:
                        isOut = False

                    if isActed == False:
                        new_events.append(
                                dict(event='new_message', type=msg_type, date=event[4], is_out=isOut, message_id=event[1], args=args, is_command=isCommand, peer_id=event[3],
                                     from_id=from_id, body=event, is_acted=isActed, attachments=attachments))
                    else:
                        new_events.append(dict(event='new_action', message_id=event[1], date=event[4], attachments=attachments, peer_id=event[3], type=msg_type, is_out=isOut, from_id=from_id, is_acted=isActed,
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

                # self.details = self.getPollingDetails()

    def polling(self, enable_notifications=False):
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
            {'name': 'polling', 'object': self.PollingRequesting},
            {'name': 'details', 'object': self.updatingDetails}]

        if enable_notifications:
            tasks.append({'name': 'notifications', 'object': self.NotificationPolling})

        for task in tasks:
            thread = Thread(name=task['name'], target=task['object'], args=())
            thread.start()

    def NotificationPolling(self):
        """

        :return:
        """
        if self.token_type == 'group':
            print('Для токена сообществ не доступен тип эвентов `new_notification`.')
            return False

        self.notify_events = []
        start_time = self.api.notifications.get(count=0)['last_viewed']

        while self.token_type == 'user':
            sleep(0.34)
            notify_body = self.api.notifications.get(count=100, start_time=start_time)
            if notify_body['count'] > 0:
                self.notify_events = notify_body['items']
                start_time = self.notify_events[0]['date'] + 1

                new_events = []
                for notify in self.notify_events:
                    print(notify)

                    user_id = None
                    user_ids = None

                    if notify['feedback'].get('items'):
                        user_ids = []
                        for user in notify['feedback']['items']:
                            user_ids.append(user.get("from_id"))
                    else:
                        user_id = notify['feedback']['from_id']
                    type = notify['type']
                    date = notify['date']
                    body = notify['feedback']
                    parent = notify['parent']
                    parent_id = notify['parent']['id']

                    if user_id:
                        new_events.append(
                            dict(user_id=user_id, type=type, date=date, body=body, parent=parent, parent_id=parent_id))
                    else:
                        new_events.append(dict(user_ids=user_ids, type=type, date=date, body=body, parent=parent,
                                               parent_id=parent_id))

                for event in new_events:
                    self.poll.emit('new_notification', event)

    def sendAudioMessage(self, files):
        """

        Отправка аудио, как голосовые сообщения в личные сообщения

        :param files: - Список имен файлов, которые нужно загрузить и отправить
        :return: - Вернет список с JSON-схемами, хранящие информацию о загруженных аудиозаписей
        """
        getUploadServer = self.api.docs.getUploadServer(type="audio_message")
        upload_url = getUploadServer["upload_url"].replace("\\", "")
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

        :param files: - Список имен файлов, которые нужно загрузить и отправить
        :return: - Вернет список с JSON-схемами, хранящие информацию о загруженных видеороликах
        """
        getUploadServer = self.api.video.save(name='SuperCraft', description='SuperCraft', is_private=False)
        upload_url = getUploadServer["upload_url"].replace("\\", "")
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

        :param files: - Список имен файлов, которые нужно загрузить и отправить
        :return: - Вернет список с JSON-схемами, хранящие информацию о загруженных фотографиях
        """
        getUploadServer = self.api.photos.getMessagesUploadServer()
        upload_url = getUploadServer["upload_url"].replace("\\", "")
        result = []
        for file in files:
            try:
                up_res = requests.post(upload_url, files={'file': open(file, "rb")})
                up_res = eval(up_res.text)
                sleep(0.34)
                getVKFile = self.api.photos.saveMessagesPhoto(photo=up_res["photo"], server=up_res["server"], hash=up_res["hash"])
                getVKFile = "photo" + str(getVKFile[0]['owner_id']) + "_" + str(getVKFile[0]['id'])
                result.append(getVKFile)
            except Exception as error:
                self.poll.emit('error', {'body': str(error)})
        return result

    def setGroupBanner(self, group_id, file, x1=0, y1=0, x2=1590, y2=400):
        """

        :param group_id: - ID сообщества VK
        :param file: - Файл с обложкой для сообщества

        :param x1: - Первая координата по оси X  |
        :param y1: - Певрая координата по оси Y _| координаты верхнего левого угла
        :param x2: - Втора координата по оси X   |
        :param y2: - Вторая координата по оси Y _| координаты нижнего правого угла
        :return:
        """

        url = self.api.photos.getOwnerCoverPhotoUploadServer(group_id=group_id, crop_x=x1, crop_y=y1, crop_x2=x2, crop_y2=y2)
        url['upload_url'] = re.sub(r'\\/', '/', url['upload_url'])

        response = eval(requests.post(url['upload_url'], files={'photo': open(file, 'rb')}).text)
        return self.api.photos.saveOwnerCoverPhoto(hash=response['hash'], photo=response['photo'])

    def setChatPhoto(self, chat_id, file, x, y, width):
        """

        :param chat_id: - ID беседы
        :param file: - Файл с фотографией беседы
        :param x: - Первая координата по оси X  |
        :param y: - Вторая координата по оси Y _| координаты верхнего левого угла
        :param width: - Ширина фотографии
        :return:
        """
        url = self.api.photos.getChatUploadServer(chat_id=chat_id, crop_x=x, crop_y=y, widht=width)
        url['upload_url'] = re.sub(r'\\/', '/', url['upload_url'])

        response = eval(requests.post(url['upload_url'], files={'file': open(file, 'rb')}).text)
        return self.api.messages.setChatPhoto(file=response['response'])

    def uploadPhotoToAlbum(self, album_id, files=[], group_id=None):
        """

        Загрузка фотографий в альбом

        :param album_id: - ID альбома
        :param files: - Спискок из имен файлов для загрузки (максимум - 5)
        :param group_id: - ID сообщества. Если не указан, фотографии будут загружены в альбом на стену пользователю
        :return:
        """

        data = {}
        for i in range(len(files)):
            data['file{}'.format(i+1)] = open(files[i], 'rb')

        if len(files) > 0:
            url = self.api.photos.getUploadServer(group_id=group_id, album_id=album_id)
            url['upload_url'] = re.sub(r'\\/', '/', url['upload_url'])

            response = eval(requests.post(url['upload_url'], files=data).text)

            if group_id:
                photos = self.api.photos.save(
                    album_id=album_id,
                    group_id=group_id,
                    server=response['server'],
                    photos_list=response['photos_list'],
                    hash=response['hash'],
                    aid=response['aid']
                )
            else:
                photos = self.api.photos.save(
                    album_id=album_id,
                    user_id=self.bot_id,
                    server=response['server'],
                    photos_list=response['photos_list'],
                    hash=response['hash'],
                    aid=response['aid']
                )

            true_photos = []
            for photo in photos:
                true_photos.append('photo{}_{}'.format(photo['owner_id'], photo['id']))

            return true_photos

    def uploadPhotoToWall(self, file, description='', group_id=None):
        """

        Загрузка фотографий на стену

        :param file: - Имя файла для загрузки
        :param description: - Описание фотографии
        :param group_id: - ID сообщества. Если не указан, фотографии будут загружены на стену пользователю.
        :return: photo<owner_id>_<id>
        """

        url = self.api.photos.getWallUploadServer(group_id=group_id)
        url['upload_url'] = re.sub(r'\\/', '/', url['upload_url'])

        response = eval(requests.post(url['upload_url'], files={'photo': open(file, 'rb')}).text)

        photo = self.api.photos.saveWallPhoto(
            group_id=group_id,
            hash=response['hash'],
            server=response['server'],
            photo=response['photo'],
            caption=description
        )

        return 'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])


    def setAvatar(self, file, x, y, width, owner_id=None):
        """

        Загрузка главной фотографии пользователя или сообщества

        :param file: - Имя файла для загрузки
        :param x: - Первая координата по оси X  |
        :param y: - Первая координата по оси Y _| координаты верхнего левого угла
        :param width: - Ширина желаемой миниатюры
        :param owner_id: - ID владельца. По умолчанию стоит ID текущего пользователя.

        Для пользователей используйте схему:     <owner_id>
        Для групп используйте схему:            -<owner_id>
        :return:
        """

        url = self.api.photos.getOwnerPhotoUploadServer(owner_id=owner_id)
        url['upload_url'] = re.sub(r'\\/', '/', url['upload_url'])

        response = eval(requests.post(url['upload_url'], files={
            'photo': open(file, 'rb'),
            '_square_crop ': '{},{},{}'.format(x, y, width)}).text)

        return self.api.photos.saveOwnerPhoto(
            server=response['server'],
            hash=response['hash'],
            photo=response['photo']
        )

    def uploadAudio(self, file, artist='VK Advanced API', title='Sound uploaded via vk_advanced_api'):
        """

        Загрузка аудиозаписей

        :param file: - Имя файла для загрузки
        :param artist: - Названия исполнителя трека
        :param title: - Название трека
        :return: audio<owner_id>_<id>
        """

        if self.token_type == 'group':
            return 'Данный метод не доступен для токена сообществ.'
        url = self.api.audio.getUploadServer()
        url['upload_url'] = re.sub(r'\\/', '/', url['upload_url'])

        response = eval(requests.post(url['upload_url'], files={'file': open(file, 'rb')}).text)

        audio =  self.api.audio.save(
            server=response['server'],
            hash=response['hash'],
            audio=response['audio'],
            artist=artist,
            title=title
        )

        return 'audio{}_{}'.format(audio['owner_id'], audio['id'])
