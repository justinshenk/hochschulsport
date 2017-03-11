from pickle import load, dump

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
    
class CourseManager(object):

    @classmethod
    def load_all(cls, fname):
        try:
            with open(fname, mode='rb') as file:
                return load(file)
        except IOError:
            raise RuntimeError('Could not read from {}'.format(fname))

    @classmethod
    def save_all(cls, courses, fname):
        try:
            with open(fname, mode='wb') as file:
                dump(courses, file)
        except IOError:
            raise RuntimeError('Could not write to {}'.format(fname))
