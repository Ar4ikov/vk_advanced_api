class Request():
    def __init__(self, method, cls, id, **params):
        self.method = method or None
        self.cls = cls
        self.id = id or None
        self.params = params