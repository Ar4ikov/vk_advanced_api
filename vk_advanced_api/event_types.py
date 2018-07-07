# | Created by Ar4ikov
# | Время: 05.07.2018 - 13:05


class Attachments:
    def __init__(self, objects: list) -> None:
        super().__init__()
        self.__objects = objects

    def get(self):
        return self.__objects


class Act:
    def __init__(self, act_type, act_from, act_mid, act_text) -> None:
        """

        :param act_type: Тип события
        :param act_from: Id юзера, который совершил событие
        :param act_mid: Id юзера, над которым совершили событие
        :param act_text: Текст события
        :param attachments: - Вложения события
        """
        super().__init__()
        self.act_type = act_type
        self.act_from = act_from
        self.act_mid = act_mid
        self.act_text = act_text


class Message:
    def __init__(self, id, group_id, type, from_id, is_out, peer_id, is_command, command, text, date,
                 important, admin_author_id, is_hidden, is_acted, act: Act, attachments: Attachments) -> None:
        """

        :param id: Id сообщения
        :param group_id: Id группы
        :param from_id: Id пользователя, который отправил сообщения
        :param is_out: 1 - если сообщение исходящее, 0 - если входящее
        :param peer_id: Id диалога
        :param is_command: Является ли командой
        :param command: Команда
        :param text: Текст сообщения
        :param date: Дата отправки
        :param is_acted: Содержит ли события беседы
        :param act: Событие беседы (Содержит класс Act с пустой информацией, если события нет)
        :param attachments: Вложения (Содержит класс Attachments с пустой информацией, если вложений нет)
        """
        super().__init__()
        self.id = id
        self.group_id = group_id
        self.type = type
        self.from_id = from_id
        self.is_out = is_out
        self.peer_id = peer_id
        self.is_command = is_command
        self.command = command
        self.text = text
        self.args = text.split(" ")
        self.date = date
        self.important = important
        self.admin_author_id = admin_author_id
        self.is_hidden = is_hidden
        self.is_acted = is_acted
        self.act = act
        self.attachments = attachments


class Join:
    def __init__(self, group_id, user_id, join_type) -> None:
        """

        :param group_id: Id группы
        :param user_id: Id пользователя, котоый вступил в сообщество
        :param join_type: Тип присоединения (`join` или `invite`)
        """
        super().__init__()
        self.group_id = group_id
        self.user_id = user_id
        self.join_type = join_type


class Leave:
    def __init__(self, group_id, user_id, self_leave) -> None:
        """

        :param group_id: Id группы
        :param user_id: Id пользователя, котоый покинул в сообщество
        :param self_leave: Тип выхода (1 - если покинул группу сам, 0 - по другой причине: kick, ban)
        """
        super().__init__()
        self.group_id = group_id
        self.user_id = user_id
        self.self_leave = self_leave


class CallbackEvent:
    def __init__(self, data) -> None:
        super().__init__()
        self.data = data

    def __getattr__(self, item):
        return self.data[item]

    def __dict__(self):
        return self.date
