import os
from speaksynk_flow_processor.interfaces.IFlow import IFlow
from speaksynk_flow_processor.interfaces.IProcessor import IProcessor
from speaksynk_flow_processor.constants.constants import FILE_NAME_ENVIROMENT_NAME
from speaksynk_flow_processor.utils.utils import mapFileNameToUser
from speaksynk_flow_processor.utils.logger import logger


class SpeakSynkFlowProcessor(IFlow, IProcessor):
    def __init__(self) -> None:
        super().__init__()
        self._file_name = os.environ[FILE_NAME_ENVIROMENT_NAME]
        self._user = mapFileNameToUser(self._file_name)
        self._logger = logger
        self._identifier = os.environ[FILE_NAME_ENVIROMENT_NAME].replace(".mp4", "")
        self._file_path = None

    def download(self, filekey):
        self._logger.info("Executing Download Method")
        return super().download(filekey)

    def run(self):
        self._logger.info("Executing Run Method")
        return super().run()

    def upload(self, filekey, fileName):
        self._logger.info("Executing Upload Method")
        return super().upload(filekey, fileName)
