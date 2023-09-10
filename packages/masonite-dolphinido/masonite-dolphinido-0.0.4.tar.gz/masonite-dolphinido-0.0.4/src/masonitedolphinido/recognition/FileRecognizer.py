from masonitedolphinido.audiofile import AudioFile
from .BaseRecognizer import BaseRecognizer


class FileRecognizer(BaseRecognizer):

    def __init__(self, dolphinido):
        super().__init__(dolphinido)

    def recognize(self, file_path: str, limit: int = 20):
        channels, _  = AudioFile.read(file_path, limit=limit)
        return self._recognize(*channels)