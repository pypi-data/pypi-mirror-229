from masonitedolphinido.models import Audio

class AudioMatch:

    def __init__(self, audio: Audio, offset: int, offset_seconds: int, confidence: int):
        self.audio = audio
        self.offset = offset
        self.offset_seconds = offset_seconds
        self.confidence = confidence

