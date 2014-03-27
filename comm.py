__author__ = 'INSPIRON14R'

import pyaudio
import threading
import socket
import wave
# import time
import Queue


class Text(threading.Thread):
    def __init__(self, client_mode, param):
        threading.Thread.__init__(self)

        self.daemon = True
        self.client_mode = client_mode
        self.queue_lock = threading.Lock()
        self.queue_msg = Queue.Queue(64)
        self.addr = param['clientaddr']
        self.port = param['clientport'][0]

        if client_mode:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind((param['destaddr'], param['clientport'][0]))

    def run(self):
        if self.client_mode:
            while True:
                msg = raw_input('>>> ')
                self.s.sendto(msg, (self.addr, self.port))
        else:
            while True:
                dat, addr = self.s.recvfrom(1024)
                print '>>> ', addr, ':', dat

    def get_message(self):
        """Fetch a text mesage"""
        self.queue_lock.acquire()
        d1 = self.queue_msg.get()
        self.queue_lock.release()
        return d1

    def put_message(self, msg):
        "put a text string in the queue"
        self.queue_lock.acquire()
        self.queue_msg.put(msg)
        self.queue_lock.release()


class Voice(threading.Thread):
    def __init__(self, client_mode, param):
        threading.Thread.__init__(self)

        self.param = param
        self.client_mode = client_mode
        self.addr = param['clientaddr']
        self.port = param['clientport'][0]

        self.enabled = True
        self.daemon = True
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=param['channels'],
                                  rate=param['rate'],
                                  frames_per_buffer=param['frames_per_buffer'],
                                  input=True,
                                  output=True)

        if client_mode:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((param['destaddr'], param['clientport'][0]))

    def run(self):
        if self.client_mode:
            while True:
                if self.enabled:
                    data = self.stream.read(self.param['frames_per_buffer'])
                    self.sock.sendto(data[:1024], (self.addr, self.port))
                    self.sock.sendto(data[1024:], (self.addr, self.port))

        else:
            while True:
                if self.enabled:
                    data, addr = self.sock.recvfrom(1024)
                    self.stream.write(data)


class FileAudio(threading.Thread):
    def __init__(self, client_mode, param):
        threading.Thread.__init__(self)

        self.param = param
        self.client_mode = client_mode
        self.addr = param['clientaddr']
        self.port = param['clientport'][0]

        self.enabled = True
        self.daemon = True

        self.wf = wave.open('sample.wav', 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=2,
                                  rate=44100,
                                  frames_per_buffer=256,
                                  output=True)

        if client_mode:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((param['destaddr'], 4000))

    def run(self):
        if self.client_mode:
            while True:
                if self.enabled:
                    data = self.wf.readframes(256)
                    if len(data) == 0:
                        break
                    self.sock.sendto(data, (self.addr, self.port))

        else:
            while True:
                if self.enabled:
                    data, addr = self.sock.recvfrom(1024)
                    self.stream.write(data)
