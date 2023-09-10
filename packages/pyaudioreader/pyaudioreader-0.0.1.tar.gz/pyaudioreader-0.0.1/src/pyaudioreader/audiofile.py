import os
import numpy as np
from pydub import AudioSegment
from pydub.utils import audioop
from hashlib import sha256


class AudioFile:

    @staticmethod
    def read(audio_file, limit: int = None):
        channels = None
        frame_rate = None

        if not audio_file.endswith(".mp3"):
            raise Exception('File should be MP3 file')

        try:
            audiofile = AudioSegment.from_file(audio_file)

            if limit:
                audiofile = audiofile[:int(limit) * 1000]

            data = np.frombuffer(audiofile.raw_data, np.int16)

            channels = []
            for channel in range(audiofile.channels):
                channels.append(data[channel::audiofile.channels])

            frame_rate = audiofile.frame_rate

        except audioop.error:
            pass

        return channels, frame_rate

    @staticmethod
    def get_name(audio_file: str) -> str:
        return os.path.splitext(os.path.basename(audio_file))[0]

    @staticmethod
    def get_hash(audio_file, blocksize=2**20):

        sha_algo = sha256()

        with open(audio_file, "rb") as f:
            while True:
                buffer = f.read(blocksize)
                if not buffer:
                    break

                sha_algo.update(buffer)

        return sha_algo.hexdigest().upper()

