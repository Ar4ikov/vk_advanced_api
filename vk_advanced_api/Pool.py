from vk_advanced_api import API
from vk_advanced_api.Response import Response
from threading import Thread
import time

class Pool():
    pool = []
    processed = []
    started = False
    id = 1

    @staticmethod
    def PoolBody():
        while True:
            i = 0
            for request in Pool.pool:
                i += 1
                Pool.id += 1
                print(len(Pool.pool))
                MakingRequest = API.API_Constructor.getRequestingBody()
                time.sleep(0.34)
                response = MakingRequest(request.cls, method=request.method, **request.params)
                Pool.processed.append(Response(body=response, id=request.id))
                if len(Pool.pool) > 0:
                    Pool.pool.remove(request)
    @staticmethod
    def startPool():
        if not Pool.started:
            Pool.started = True
            Thread(target=Pool.PoolBody, name="RequestPool", args=()).start()

    @staticmethod
    def getActualId():
        return Pool.id

    @staticmethod
    def addTask(Pool, request):
        Pool.pool.append(request)