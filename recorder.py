# -*- coding: iso-8859-1 -*-
import logging
import pyaudio
import wave
import os

from kalliope.core.NeuronModule import NeuronModule, InvalidParameterException
from kalliope.core.Utils.Utils import Utils
from kalliope.core.PlayerLauncher import PlayerLauncher
from kalliope.core.ConfigurationManager import SettingLoader
from kalliope.core.HookManager import HookManager
from ctypes import *
from contextlib import contextmanager



class Recorder(NeuronModule):
    def __init__(self, **kwargs):
        super(Recorder, self).__init__(**kwargs)
        # the args from the neuron configuration
        self.rate = kwargs.get('rate', 44100)
        self.chunk = kwargs.get('chunk', 1024)
        self.channels = kwargs.get('channels', 2)
        self.seconds = kwargs.get('seconds', None)
        self.file_name = kwargs.get('file_name', 'default.wav')
        self.playback = kwargs.get('playback', False)
        self.format = kwargs.get('format', None)
        # check if parameters have been provided
        if self._is_parameters_ok():
            self.output = os.path.dirname(__file__) + "/output/" + self.file_name
            if self.playback:
                sl = SettingLoader()
                self.settings = sl.settings
                self.player = PlayerLauncher.get_player(settings=self.settings)
            if self.seconds:
                self.start_recording()
            if self.playback and not self.seconds:
                self.playback_file(self.output)

    def start_recording(self):
        # pyaudio can work but alsa-lib spiting out error messages, to avoid this I used a method to suppress the messages found on stackoverflow
        # https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
        
        with self.noalsaerr():
            audio = pyaudio.PyAudio()
        
        FORMAT = pyaudio.paInt32
        if self.format == "paInt16":
            FORMAT = pyaudio.paInt16
        if self.format == "paInt24":
            FORMAT = pyaudio.paInt24


        stream = audio.open(format=FORMAT, channels=self.channels,
                        rate=self.rate, input=True,
                        frames_per_buffer=self.chunk)
                        
        Utils.print_info("[ Recorder ] Is recording...")
        HookManager.on_start_listening()
        frames = []
     
        for i in range(0, int(self.rate / self.chunk * self.seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        audio.terminate()
        HookManager.on_stop_listening()
        waveFile = wave.open(self.output, 'wb')
        waveFile.setnchannels(2)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(self.rate)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()
        Utils.print_info("[ Recorder ] Record saved to %s" % self.output)
        
        if self.playback:
            self.playback_file(self.output)
    
    def playback_file(self, output):
        if os.path.isfile(output):
            Utils.print_info("[ Recorder ] Playback %s" % output)
            return self.player.play(output)
        else:
            if self.file_name == "default.wav":
                Utils.print_info("[ Recorder ] Nothing to play")
            else:
                Utils.print_info("[ Recorder ] %s not found" % output)
    
    def py_error_handler(self, filename, line, function, err, fmt):
        pass

    
    @contextmanager
    def noalsaerr(self):
        asound = cdll.LoadLibrary('libasound.so')
        ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
        c_error_handler = ERROR_HANDLER_FUNC(self.py_error_handler)
        asound.snd_lib_error_set_handler(c_error_handler)
        yield
        asound.snd_lib_error_set_handler(None)            

        
    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the neuron
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: InvalidParameterException, MissingParameterException
        """
        if self.seconds:
            try:
                self.seconds = int(self.seconds)
            except ValueError:
                raise InvalidParameterException('[ Recorder ] %s is not a valid integer' % self.seconds)
        return True
