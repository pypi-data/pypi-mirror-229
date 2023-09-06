import boto3
import os
from speaksynk_flow_processor.SpeakSynkFlowProcessor import SpeakSynkFlowProcessor
from speaksynk_flow_processor.utils.utils import createFolder
from speaksynk_flow_processor.constants.constants import WORKING_DIR, VIDEO_FILE_NAME, S3_BUCKET_NAME

class AWSSpeakSynkFlowProcesor(SpeakSynkFlowProcessor):
    
    def __init__(self):
        super().__init__()
        self.s3 = boto3.client('s3')
        self.bucket_name = os.environ[S3_BUCKET_NAME]
    
    def download(self):
        super().download()
        createFolder(WORKING_DIR)
        self._logger.info("File created")
        filePath = os.path.join(WORKING_DIR, VIDEO_FILE_NAME)
        self._file_path = f"video/{self._identifier}.mp4"
        self._logger.info("Video path: %s, Video Key: %s" % (filePath, self._file_path))
        with open(filePath, 'wb') as video:
            self.s3.download_fileobj(self.bucket_name, self._file_path, video)
    
    def upload(self, filename):
        super().upload(filename)
        with open(self._file_path, "rb") as out_video:
            self._logger.info("Uploading video: %s" % filename)
            self.s3.upload_fileobj(out_video, self.bucket_name, filename)	
            self._logger.info("Finished uploaded video")