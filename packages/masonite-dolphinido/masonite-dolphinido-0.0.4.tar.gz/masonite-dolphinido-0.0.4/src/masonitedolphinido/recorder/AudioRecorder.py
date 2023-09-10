import numpy
import pyaudio


class AudioRecorder:
    CHUNKSIZE = 8192
    CHANNELS = 2
    SAMPLERATE = 44100
    FORMAT = pyaudio.paInt16

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.channels = AudioRecorder.CHANNELS
        self.chunksize = AudioRecorder.CHUNKSIZE
        self.samplerate = AudioRecorder.SAMPLERATE
        self.audioformat = AudioRecorder.FORMAT
        self.duration = None
        self.stream = None
        self.data = []
       
    def record(self, seconds):
        self.duration = seconds
        self.__start_recording()
        self.__capture_recording()
        self.__stop_recording()

    def getdata(self):
        return self.data

    def gettime(self):
        return len(self.data[0]) / self.samplerate

    def __init_data(self):
        self.data = [[] for _ in range(self.channels)]

    def __start_recording(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = self.pyaudio.open(
            format=self.audioformat,
            channels=self.channels,
            rate=self.samplerate,
            input=True,
            frames_per_buffer=self.chunksize,
        )
        self.__init_data()

    def __stop_recording(self) -> None:
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

    def __capture_recording(self) -> None:

        for _ in range(0, int(self.samplerate / self.chunksize * int(self.duration))):
            data = self.stream.read(self.chunksize)

            np_data = numpy.frombuffer(data, numpy.int16)

            for channel in range(self.channels):
                self.data[channel].extend(np_data[channel::self.channels])



