from masonitedolphinido.config import fingerprint as config
from .AudioMatch import AudioMatch

class BaseRecognizer(object):

    def __init__(self, dolphinido):
        self.dolphinido = dolphinido

    def recognize(self, **kwargs):
        pass

    def _recognize(self, *data):
        matches = []
        for _ , channel in enumerate(data):
            fingerprints = self.dolphinido.fingerprint_audio(channel)
            matches.extend(self.__find_matches(fingerprints))
        total_matches = len(matches)
        if total_matches > 0:
            match = self.__highest_match(matches)
            return match

    def __find_matches(self, fingerprints):
        mapper = dict()
        for fingerprint, offset in fingerprints:
            mapper[fingerprint] = offset
        values = mapper.keys()

        matches = self.dolphinido.find_matches(list(values))

        for match in matches:
            offset_diff = match.offset - mapper[match.fingerprint]
            yield match.audio_id, offset_diff

    def __highest_match(self, matches):

        diff_counter = {}
        offset = 0
        confidence = 0
        match_id = None

        for match in matches:
            audio_id, diff = match
            if diff not in diff_counter:
                diff_counter[diff] = {}

            if audio_id not in diff_counter[diff]:
                diff_counter[diff][audio_id] = 0

            diff_counter[diff][audio_id] += 1
            if diff_counter[diff][audio_id] > confidence:
                offset = diff
                confidence = diff_counter[diff][audio_id]
                match_id = audio_id

        offset_seconds = round(float(offset) / config.DEFAULT_FS *
                               config.DEFAULT_WINDOW_SIZE *
                               config.DEFAULT_OVERLAP_RATIO, 5)
        
        audio = self.dolphinido.find_audio(match_id)
        
        return AudioMatch(
            audio=audio,
            offset=offset,
            offset_seconds=offset_seconds,
            confidence=confidence
        )

