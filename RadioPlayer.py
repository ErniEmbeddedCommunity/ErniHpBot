"""Module for playing audio files over FM"""
import os
from threading import Lock, Thread, Condition
from time import sleep
from collections import deque
from subprocess import Popen, PIPE, STDOUT
import shlex

class FmPlayer(Thread):
    """Plays files over FM"""
    freq = "87.0"
    _condition = Condition()

    _playlist = deque()
    class FileInfo:
        """Data holder for play files"""
        def __init__(self, file_name, delete_after_convert=True ,delete_after_play=False):
            self._file_name = file_name
            self._delete_after_convert = delete_after_convert
            self._delete_after_play = delete_after_play
        def file_name(self):
            return self._file_name
        def rename(self, new_name):
            self._file_name = new_name
        def delete_after_play(self):
            return self._delete_after_play
        def delete_after_convert(self):
            return self._delete_after_convert
        def __str__(self):
            return self.file_name()

    @classmethod
    def play_file(cls, file_name, delete_after_play = True, delete_after_convert = True):
        cls._condition.acquire()
        print("Added new file to the playlist")
        cls._playlist.append(FmPlayer.FileInfo(file_name,delete_after_convert=delete_after_convert,delete_after_play=delete_after_play))
        cls._condition.notify()
        cls._condition.release()
            
    @classmethod
    def _play_file(cls, file_info: FileInfo):
        print("Playing " + file_info.file_name())
        wav_file = cls._convert_file_to_wav(file_info)
        print("File converted to wav " + str(wav_file))
        cls._launch_transmiter(cls.freq,wav_file)
        print("File played")
    
    def run(self):
        print("FM PLAYER THREAD STARTED")
        while True:
            self._condition.acquire()
            if not self._playlist:
                print ("Nothing to play")
                self._condition.wait()
                print ("file added")
            next_file = self._playlist.popleft()
            self._condition.release()
            self._play_file(next_file)

    @staticmethod
    def _convert_file_to_wav(file_info: FileInfo):
        command = "avconv -i " + str(file_info) + " " + str(file_info) + ".wav -y"
        avconv_process = Popen(shlex.split(command), stderr=STDOUT)
        avconv_process.wait()
        
        if file_info.delete_after_convert():
            os.remove(str(file_info))
        file_info.rename(str(file_info) + ".wav")
        return file_info

    @staticmethod
    def _launch_transmiter(freq, file_info: FileInfo):
        sox_process = Popen(shlex.split("sox " + str(file_info)+ " -t wav -"), stderr=STDOUT, stdout=PIPE)
        fm_transmitter_process = Popen(shlex.split("sudo fm_transmitter/fm_transmitter -f "+ freq + " - "),stderr=STDOUT, stdin=sox_process.stdout )
        fm_transmitter_process.wait()
        if file_info.delete_after_play():
            os.remove(str(file_info))


FMPLAYER = FmPlayer()
FMPLAYER.start()
