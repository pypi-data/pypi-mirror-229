from abc import abstractmethod


class IFlow():

    @abstractmethod
    def download(self):
        pass

    @abstractmethod
    def upload(self, filaname):
        pass