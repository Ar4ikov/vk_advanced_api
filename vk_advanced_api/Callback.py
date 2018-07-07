# | Created by Ar4ikov
# | Время: 22.06.2018 - 15:26

from flask import Flask, request, json

from vk_advanced_api.data_proc import DataProcessing


class Callback(Flask):
    def __init__(self, event_poll, host="127.0.0.1", secret_key=None, confirmation_key=None, debug=False,
                 import_name=__name__):
        super().__init__(import_name)

        self.event_pool = event_poll

        self.port = 80  # VK не разрешает делать иначе, только 80 порт
        self.host = host
        self.debug = debug

        self.confirmation_key = confirmation_key  # Одноразовый ключ подтверждения CallBack сервера.
        self.secret_key = secret_key  # Secret Key - уникальный защитный ключ, который ВК передает на CallBack сервер.

        self.data_proc = DataProcessing(self.event_pool, "")

    def set_start_params(self, host):
        self.host = host

    def run(self, **kwargs):
        @self.route("/robots.txt")
        def robots():
            return \
                "User-agent: *\n" \
                "Disallow: /"

        @self.route("/callback", endpoint="callback", methods=["POST"])
        def callback():
            data = json.loads(request.data)

            if data.get("secret") != "your-secret-key":
                return "Invalid secret key!"

            return self.data_proc.emit(data)

        super().run(host=self.host, port=self.port, debug=self.debug, **kwargs)
