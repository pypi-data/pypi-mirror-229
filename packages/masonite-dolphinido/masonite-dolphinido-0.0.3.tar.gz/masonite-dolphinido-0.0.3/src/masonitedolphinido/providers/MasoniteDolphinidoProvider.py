from masonite.packages import PackageProvider
from masonitedolphinido.commands import *

class MasoniteDolphinidoProvider(PackageProvider):

    def configure(self):
        self.root("masonitedolphinido")\
        .name("masonitedolphinido")\
        .config("config/fingerprint.py", publish=True)\
        .migrations(
            "migrations/create_audios_table.py", 
            "migrations/create_audio_fingerprints_table.py"
        )\
        .commands(
            FingerprintCommand,
            RadioCommand,
            RecogFileCommand,
            RecogMicCommand,
            RecogRadioCommand
        )

    def boot(self):
        pass
