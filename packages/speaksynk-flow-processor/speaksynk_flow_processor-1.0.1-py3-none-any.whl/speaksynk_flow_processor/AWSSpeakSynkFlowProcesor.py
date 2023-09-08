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
    
    def download(self, filekey, filename):
        super().download(filekey, filename)
        createFolder(WORKING_DIR)
        self._logger.info("File created")
        filePath = os.path.join(WORKING_DIR, filename)
        # self._file_path = f"video/{self._identifier}.mp4"
        self._logger.info("Video path: %s, Video Key: %s" % (filePath, filekey))
        with open(filePath, 'wb') as handle:
            self.s3.download_fileobj(self.bucket_name, filekey, handle)
    
    def upload(self, filekey, filename):
        super().upload(filekey, filename)
        filePath = os.path.join(WORKING_DIR, filename)
        with open(filePath, "rb") as out_video:
            self._logger.info("Uploading video: %s" % filekey)
            self.s3.upload_fileobj(out_video, self.bucket_name, filekey)	
            self._logger.info("Finished uploaded video")
