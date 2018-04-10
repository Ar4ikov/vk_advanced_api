from uuid import uuid4 as UUID

class Request():
    def __init__(self, method, cls, id, **params):
        """

        Request class, который является прямым телом запроса

        :param method: - Метод API VK
        :param cls: - class API (API.py -> API_Constructor)
        :param id: - ID запроса
        :param uuid: - UUID запроса
        :param params: - Параметры запроса к API VK
        """
        self.method = method
        self.cls = cls
        self.id = id
        self.params = params

    def getCls(self):
        return self.cls

    def getId(self):
        return self.id

    def getMethod(self):
        return self.method

    def getParams(self):
        return self.params