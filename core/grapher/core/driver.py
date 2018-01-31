import abc


class DriverManager:
    def get_driver(self, name):
        pass


class AbstractDriver(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def data(self, types, links=None):
        pass

    @abc.abstractmethod
    def info(self):
        pass
