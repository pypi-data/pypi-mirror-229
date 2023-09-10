import numpy
import pyaudio


class Microphone:
    SAMPLE_RATE = 44100
    SAMPLE_SIZE = 8192
    CHANNELS = 2
    FORMAT = pyaudio.paInt16

    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.sample_rate = Microphone.SAMPLE_RATE
        self.sample_size = Microphone.SAMPLE_SIZE
        self.channels = Microphone.CHANNELS
        self.audio_format = Microphone.FORMAT
        self.duration = None
        self.stream = None
        self.data = []
    
    def set_channels(self, channels):
        self.channels = channels

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def set_sample_size(self, sample_size):
        self.sample_size = sample_size   

    def record(self, seconds=20):
        self.duration = seconds
        self.__start_recording()
        self.__capture_recording()
        self.__stop_recording()

    def getdata(self):
        return self.data

    def gettime(self):
        return len(self.data[0]) / self.sample_rate

    def __init_data(self):
        self.data = [[] for _ in range(self.channels)]

    def __start_recording(self) -> None:
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.stream = self.pyaudio.open(
            format=self.audio_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.sample_size,
        )
        self.__init_data()

    def __stop_recording(self) -> None:
        self.stream.stop_stream()
        self.stream.close()
        self.pyaudio.terminate()

    def __capture_recording(self) -> None:

        for _ in range(0, int(self.sample_rate / self.sample_size * int(self.duration))):
            data = self.stream.read(self.sample_size)

            np_data = numpy.frombuffer(data, numpy.int16)

            for channel in range(self.channels):
                self.data[channel].extend(np_data[channel::self.channels])



