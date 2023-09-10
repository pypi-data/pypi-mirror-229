from AWSSpeakSynkFlowProcesor import AWSSpeakSynkFlowProcesor
class Implementation(AWSSpeakSynkFlowProcesor):
    def __init__(self):
        super().__init__()
        self.filekey = 'break_time/%s' % self._identifier
    def download(self):
        return super().download(self.filekey)
    def run(self):
        print('prcessssss')
    def upload(self):
        super().upload(self.filekey)
    


implementation  = Implementation()
implementation.download()
implementation.run()
implementation.upload()