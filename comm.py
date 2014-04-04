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

        self.queue_lock = threading.Lock()
        self.queue_msg = Queue.Queue(64)

        self.daemon = True
        self.client_mode = client_mode

        self.addr = param['clientaddr']
        self.port = param['clientport'][0]

        self.msg = ''

        if client_mode:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind((param['destaddr'], param['clientport'][0]))

    def run(self):
        if self.client_mode:
            while True:
                # msg = raw_input('>>> ')
                if self.msg != '':
                    self.s.sendto(self.msg, (self.addr, self.port))
                    self.msg = ''
        else:
            while True:
                dat, addr = self.s.recvfrom(1024)
                # print '>>> ', addr, ':', dat
                with self.queue_lock:
                    self.queue_msg.put(dat)

    def get_message(self):
        """ Fetch a mesage from the queue
            if queue is empty, returns NoneType
            else returns str
        """
        with self.queue_lock:
            if not self.queue_msg.empty():
                d1 = self.queue_msg.get()
                return d1
            else:
                return None

    def put_message(self, msg):
        """ Sends a message
            takes a str as argument
        """
        self.msg = msg

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
