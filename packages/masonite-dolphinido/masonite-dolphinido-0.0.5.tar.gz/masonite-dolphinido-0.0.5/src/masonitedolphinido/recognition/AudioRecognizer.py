from .BaseRecognizer import BaseRecognizer

class AudioRecognizer(BaseRecognizer):

    def __init__(self, dolphinido):
        super().__init__(dolphinido)

    def recognize(self, samples):
        return self._recognize(samples)