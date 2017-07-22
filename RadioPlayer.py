
import os
from threading import Lock, Thread, Condition
from time import sleep
from collections import deque


class FmPlayer(Thread):
    """Plays files over FM"""
    freq = "87.0"
    condition = Condition()

    _playlist = deque()
    _playing = False
    
    @classmethod
    def play_file(cls, file_name):
        cls.condition.acquire()
        print("Added new file to the playlist")
        cls._playlist.append(file_name)
        cls.condition.notify()
        cls.condition.release()
            
    @classmethod
    def _play_file(cls, file_name ):
        print("Playing " + file_name)
        wav_file = cls._convert_file_to_wav(file_name)
        print("File converted to wav " + wav_file)
        cls._launch_transmiter(cls.freq,wav_file)
        print("File played")
    
    def run(self):
        print("FM PLAYER THREAD STARTED")
        while True:
            self.condition.acquire()
            if not self._playlist:
                print ("Nothing to play")
                self.condition.wait()
                print ("file added")
            next_file = self._playlist.popleft()
            self.condition.release()
            self._play_file(next_file)

    @staticmethod
    def _convert_file_to_wav(file_name):
        os.system("avconv -i " + file_name + " " + file_name + ".wav -y")
        os.remove(file_name)
        return file_name + ".wav"

    @staticmethod
    def _launch_transmiter(freq, file_name):
        os.system("sox "+file_name+" -t wav - |sudo fm_transmitter/fm_transmitter -f "+ freq + " - " )
        os.remove(file_name)


FMPLAYER = FmPlayer()

FMPLAYER.start()
