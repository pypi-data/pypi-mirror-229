from masonitedolphinido.config import fingerprint as config
from masonitedolphinido.models import Audio, AudioFingerprint
from masonitedolphinido.audiofile import AudioFile
from masonitedolphinido.fingerprint import Fingerprint
from masonitedolphinido.recognition import AudioRecognizer, FileRecognizer, MicrophoneRecognizer
from masonitedolphinido.radio import Radio

class Dolphinido:

    def __init__(self):
        self.audios = Audio()
        self.fingerprints = AudioFingerprint()

        self.fingerprint =  Fingerprint()

        self.limit = config.FINGERPRINT_LIMIT
        if self.limit == -1:
            self.limit = None

    def radio(self):
        radio = Radio()
        return radio

    def create_audio(self, audio_file, audio_id=None):
        audio_hash = AudioFile.get_hash(audio_file)

        if audio_id:
            audio = self.audios.create({
                "id": audio_id,
                "hash_id": audio_hash
            })   
        else:
            audio = self.audios.create({
                "hash_id": audio_hash
            })

        hash_count = self.create_fingerprint(audio_file)

        audio.update_hash_count(hash_count)

        return audio

    def create_fingerprint(self, audio_file):
        hash = AudioFile.get_hash(audio_file)
        audio = self.audios.get_by_hash(hash)
        hash_count = 0

        if audio and audio.hash_count is None:
            fingerprints = self.fingerprint_file(audio_file) 
            hash_count = len(fingerprints)
            self.fingerprints.insert(audio, fingerprints)
        return hash_count
        
    def fingerprint_file(self, audio_file, limit=None):
        if limit is None:
            limit = self.limit

        channels, frame_rate = AudioFile.read(audio_file, limit)
        fingerprints = set()

        for _ , channel in enumerate(channels, start=1):
            hashes = self.fingerprint.fingerprint(channel, Fs=frame_rate)
            fingerprints |= set(hashes)

        return fingerprints

    def fingerprint_audio(self, samples):
        fingerprints = self.fingerprint.fingerprint(samples)
        return fingerprints
    
    def recognize_file(self, file_path):
        recognizer = FileRecognizer(self)
        return recognizer.recognize(file_path)

    def recognize_recording(self, seconds):
        recognizer = MicrophoneRecognizer(self)
        return recognizer.recognize(seconds)
    
    def recognize_audio(self, samples):
        recognizer = AudioRecognizer(self)
        return recognizer.recognize(samples)

    def find_matches(self, fingerprints):
        return self.fingerprints.match(fingerprints)

    def find_audio(self, audio_id):
        return self.audios.get_by_id(audio_id)
    
    def audio_exists(self, audio_file):
        hash = AudioFile.get_hash(audio_file)
        audio = self.audios.get_by_hash(hash)
        if audio:
            return True
        else:
            return False