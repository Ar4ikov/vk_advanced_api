# | Created by Ar4ikov
# | Время: 22.06.2018 - 15:26
from enum import Enum
from flask import Flask, request
from pymitter import EventEmitter


# TODO: Работа над Callback API началась.

class DataTypes(Enum):
    """
    Методы поддерживаются не все. Их список будет пополняться позднее
    """
    CONFIRMATION = "confirmation"
    MESSAGE_NEW = "message_new"
    GROUP_LEAVE = "group_leave"
    GROUP_JOIN = "group_join"


class Callback(Flask):
    def __init__(self, event_pool, host="127.0.0.1", debug=False, import_name=__name__, static_url_path=None, static_folder='static', static_host=None,
                 host_matching=False,
                 subdomain_matching=False, template_folder='templates', instance_path=None,
                 instance_relative_config=False, root_path=None):
        super().__init__(import_name, static_url_path, static_folder, static_host, host_matching, subdomain_matching,
                         template_folder, instance_path, instance_relative_config, root_path)

        self.event_pool: EventEmitter = event_pool

        self.port = 80  # VK не разрешает делать иначе, только 80 порт
        self.host = host
        self.debug: bool = debug

    def set_start_params(self, host):
        self.host = host

    def run(self, **kwargs):
        """

        :param kwargs:
        :return:
        """

        @self.route("/callback", endpoint="confirm", methods=["POST"])
        def confirm():
            """
            Пока никакой пост-обработки запросов. Как ни как - тестовая ветка!

            :return:
            """
            data = request.form

            data_type = data.get("type")

            if data_type == DataTypes.CONFIRMATION:
                return "47331cf2"

            if data_type == DataTypes.MESSAGE_NEW:
                return self.event_pool.emit("new_message", data)

        super().run(host=self.host, port=self.port, debug=self.debug, **kwargs)
