from masonitedolphinido.recorder import AudioRecorder
from .BaseRecognizer import BaseRecognizer

class MicrophoneRecognizer(BaseRecognizer):

    def __init__(self, dolphinido):
        super().__init__(dolphinido)

    def recognize(self, duration: int):
        recorder = AudioRecorder()
        recorder.record(duration)
        data = recorder.getdata()
        return self._recognize(*data)





