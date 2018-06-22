from uuid import uuid4 as UUID


class Response():
    def __init__(self, body, id):
        """

        Класс ответа Response

        :param body: - Тело ответа
        :param uuid: - UUID ответа
        :param id: - Id ответа
        """
        self.body = body
        self.id = id

    def getBody(self):
        return self.body

    def getId(self):
        return self.id
