from pickle import load, dump

class Course(object):

    def __init__(self, id, name, url=None, time=None, place=None, kind='buchen',
            bs_code=None):
        self._id = id
        self._name = name
        self._url = url
        self._time = time
        self._place = place
        self._kind = kind
        self._bs_code = bs_code

    def __str__(self):
        return "{id} {name}: {time}".format(id=self.id, name=self.name, time=self.time)

    @property
    def id(self):
        return self._id

    @property
    def url(self):
        return self._url

    @property
    def name(self):
        return self._name

    @property
    def time(self):
        return self._time
    
    @property
    def place(self):
        return self._place

    @property
    def kind(self):
        return self._kind

    @property
    def bs_code(self):
        return self._bs_code
    
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
