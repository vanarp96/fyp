__author__ = 'viren'

import pyaudio
import threading
import socket
import wave


class Text(threading.Thread):
    def __init__(self, client_mode, param):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()

        self.daemon = True
        self.client_mode = client_mode
        self.addr = param['localaddress']
        self.port = param['port']

        if client_mode:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.s.bind((param[''], self.port))

    def run(self):
        self.lock.acquire()
        if self.client_mode:
            while True:
                t_queue_lock.acquire()
                msg = t_queue.get()
                t_queue_lock.release()

                #msg = raw_input()
                self.s.sendto(msg, (self.addr, self.port))
        else:
            while True:
                dat, addr = self.s.recvfrom(1024)
                #print addr, ':', dat
                t_queue_lock.acquire()
                t_queue.put(dat)
                t_queue_lock.release()

    def enable(self):
        pass

    def disable(self):
        pass



class Voice(threading.Thread):
    def __init__(self, client_mode, param):
        threading.__init__(self)

        self.param = param
        self.client_mode = client_mode
        self.addr = param['remotefwdto']
        self.port = param['udpports'][0]

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
            self.sock.bind((self.addr, self.port))

    def run(self):
        if self.client_mode:
            while True:
                if self.enabled:
                    data = self.stream.read(self.param['frames_per_buffer'])
                    self.sock.sendto(data[:1024], (self.addr, self.port))
                    self.sock.sendto(data[1024:], (self.addr, self.port))
                    # v_queue_lock.acquire()
                    # v_queue.put(data)
                    # v_queue_lock.release()

        else:
            while True:
                if self.enabled:
                    data, addr = self.sock.recvfrom(1024)
                    self.stream.write(data)
                    # v_queue_lock.acquire()
                    # self.stream.write(v_queue.get())
                    # v_queue_lock.release()

class FileAudio(threading.Thread):
    def __init__(self, client_mode, param):
        threading.__init__(self)

        self.param = param
        self.client_mode = client_mode
        self.addr = param['remotefwdto']
        self.port = param['udpports'][0]

        self.enabled = True
        self.daemon = True

        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=param['channels'],
                                  rate=param['rate'],
                                  frames_per_buffer=param['frames_per_buffer'],
                                  output=True)

        self.wf = wave.open('sample.wav', 'rb')
        self.wf.setnchannels(param['channels'])
        self.wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        self.wf.setframerate(param['rate'])

        if client_mode:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.addr, self.port))

    def run(self):
        if self.client_mode:
            while True:
                if self.enabled:
                    data = self.wf.readframes(1)
                    self.sock.sendto(data[:1024], (self.addr, self.port))
                    self.sock.sendto(data[1024:], (self.addr, self.port))

        else:
            while True:
                if self.enabled:
                    data, addr = self.sock.recvfrom(1024)
                    self.stream.write(data)
