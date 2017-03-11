class Course(object):

    def __init__(self, id, name, url=None, time=None, place=None):
        self.__id = id
        self.__name = name
        self.__url = url
        self.__time = time
        self.__place = place

    def __str__(self):
        return "{id} {name}: {time}".format(id=self.id, name=self.name, time=self.time)

    @property
    def id(self):
        return self.__id

    @property
    def url(self):
        return self.__url

    @property
    def name(self):
        return self.__name

    @property
    def time(self):
        return self.__time
    
    @property
    def place(self):
        return self.__place
