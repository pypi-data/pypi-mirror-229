from masonitedolphinido.helpers import grouper
from masoniteorm.models import Model
from .Audio import Audio


class AudioFingerprint(Model):
    __fillable__ = ['id', 'audio_id', 'fingerprint', 'offset']
    
    def match(self, fingerprints):
        return self.query().where_in('fingerprint', fingerprints).get()

    def insert(self, audio: Audio, fingerprints: set):
        values = []
        for fingerprint, offset in fingerprints:
            values.append({'audio_id': audio.id, 'fingerprint': fingerprint, 'offset': offset})
            
        for split_values in grouper(values, 1000):
            self.query().builder.new().bulk_create(split_values)
    