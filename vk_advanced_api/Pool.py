from vk_advanced_api import API

class Pool(API):
    pool = []

    @staticmethod
    def getActualId(self):
        pass

    @staticmethod
    def addTask(Pool, request):
        Pool.pool.append(request)