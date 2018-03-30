"""

    Пример #4. Загрузка фото/аудио/видео на сервера VK для отправки в сообщения

    ATTENTION! Из-за политики авторского права VK запретила общественности
    метод audio в своём API, из-за чего аудио будет загружена в виде
    голосового сообщения.

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

# Список -> Файлы для загрузки на сервер
files = ['captcha.png', 'test.jpg']

uploaded_files = api.sendPhoto(files=files)

# На выходе вы получите список со следующей структурой:
# {
#   - owner_id -> ID владельца файла VK
#   - id -> ID загруженного медиа
# }
#
# Такую же процедуру можно проделать абсолютно для всех типов файлов, как видео, так  аудио

files_1 = ['Blue_Chair.mp4', 'Do_not_go_on_bear_fucking_bitch.mp4']
uploaded_files_1 = api.sendVideo(files=files_1)

files_2 = ['voice.mp3']
uploaded_files_2 = api.sendAudioMessage(files=files_2)

# А затем это можно отправить сообщение с ними, предварительно обоаботав данные

attachments = []

for item in uploaded_files:
    attachments.append(item['owner_id'] + "_" + item['id'])

api.sendMessage(
    user_id=1,
    message='Держи, друг! Я отправил тебе фотграфии с багами Телеграма!',
    attachments=attachments
)