class Request:
    def __init__(self):
        self.__method = None
        self.__url = None
        self.__headers = None
        self.__body = None

    @property
    def method(self):
        return self.__method
