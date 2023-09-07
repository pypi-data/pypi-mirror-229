from tie_bcd_api_v2.Request import Request


class Company:
    def __init__(self):
        self.__id = None
        self.__name = None

    @property
    def id(self):
        return self.__id

    @property
    def name(self):
        return self.__name

    def __get_companies(self):
        request = Request()
        print(request.method)
        return self.__id
