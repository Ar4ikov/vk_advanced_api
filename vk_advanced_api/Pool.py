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

                MakingRequest = request.getCls().getRequestingBody()

                time.sleep(0.34)

                response = MakingRequest(request.getCls(), method=request.getMethod(), **request.getParams())
                Pool.processed.append(Response(body=response, id=request.getId()))

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

    @staticmethod
    def addRequest(request):
        Pool.pool.append(request)

    @staticmethod
    def getProcessed():
        return Pool.processed
