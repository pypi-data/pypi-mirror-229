from abc import abstractmethod


class IFlow():

    @abstractmethod
    def download(self, filekey, filename):
        pass

    @abstractmethod
    def upload(self, filekey, filename):
        pass