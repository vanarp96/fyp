__author__ = 'INSPIRON14R'

import pyaudio
import threading
import socket
import wave
# import time
import Queue
import time


class Text(threading.Thread):
    def __init__(self, client_mode, param):
        threading.Thread.__init__(self)

        self.daemon = True
        self.client_mode = client_mode

        self.addr = param['serveraddr']
        self.port = 9090
        self.conn = None
        self.msg = ''
        self.msg_list = []

        if client_mode:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            x = True
            while x:
                print 'trying to connect to', self.addr, self.port
                try:
                    self.s.connect((self.addr, self.port))
                    x = False
                except:
                    print 'server is not running'
                    print 'waiting for 5 seconds...'
                    time.sleep(5)
                
        else:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind(('', self.port))
            self.s.listen(5)

    def run(self):
        if not self.client_mode:
            self.conn, self.other_addr = self.s.accept()
            print 'connected to', self.other_addr
        
        try:
            while True:
                if not self.client_mode:
                    dat = self.conn.recv(1024)
                else:
                    dat = self.s.recv(1024)
                print 'recvd "' + dat
                self.msg_list.append(dat)
        except:
            print 'Connection unexpectedly terminated'
            sys.exit(1)

    def get_message(self):
        msg_list = self.msg_list
        self.msg_list = []
        return msg_list
        
    def put_message(self, msg):
        if self.client_mode:
            self.s.sendall(msg)
        else:
            if self.conn == None:
                print 'Connection problem'
                return
            self.conn.sendall(msg)
            print 'sent to', self.other_addr
            
#############################################################################3        
        
# class Text(threading.Thread):
    # def __init__(self, client_mode, param):
        # threading.Thread.__init__(self)
        
        # self.lock = threading.Lock()
        
        # self.daemon = True
        # self.client_mode = client_mode

        # self.addr = param['clientaddr']
        # self.port = param['clientport'][0]

        # self.msg = ''
        # self.msg_list = []

        # if client_mode:
            # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # else:
            # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.s.bind((param['destaddr'], param['clientport'][0]))

    # def run(self):
        # ### remove start
        # # if self.client_mode:
            # # while True:
                # # if self.msg != '':
                    # # self.s.sendto(self.msg, (self.addr, self.port))
                    # # self.msg = ''
        # ### remove end
        
        # # else:
            # while True:
                # with self.lock:
                    # dat, addr = self.s.recvfrom(1024)
                # self.msg_list.append(dat)
                # print '>>> ', addr, ':', dat

    # def get_message(self):
        # """ Fetch a mesage from the queue
            # if queue is empty, returns NoneType
            # else returns str
        # """
        # msg_list = self.msg_list
        # self.msg_list = []
        # return msg_list


    # def put_message(self, msg):
        # """ Sends a message
            # takes a str as argument
        # """
        # with self.lock:
            # self.s.sendto(msg, (self.addr, self.port))

############################################################################        





class Kand(threading.Thread):
    def __init__(self, client_mode, param):
        threading.Thread.__init__(self)
        self.addr = param['serveraddr']
        self.port = param['kand_port']
        self.client_mode = client_mode
        
        self.param = param
        self.enabled = False
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
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('', param['kand_port'] ))
            
    def run(self):
        if self.client_mode:
            print 'Sending'
            i = 0
            while True:
                if self.enabled:
                    print i, '\r',
                    i += 1
                    data = self.stream.read(self.param['frames_per_buffer'])
                    self.sock.sendto(data[:1024], (self.addr, self.port))
                    self.sock.sendto(data[1024:], (self.addr, self.port))
        else:
            print 'Receiving'
            i = 0
            while True:
                if self.enabled:
                    print i, '\r',
                    i += 1
                    data, addr = self.sock.recvfrom(1024)
                    self.stream.write(data)

    def enable(self):
        self.enabled = True
        
    def disable(self):
        self.enabled = False
        
    def switch(self):
        self.enabled = not self.enabled




# class Kand(threading.Thread):
    # def __init__(self, client_mode, param):
        # threading.Thread.__init__(self)
        # self.addr = param['serveraddr']
        # self.port = param['kand_port']
        # self.client_mode = client_mode
        
        # self.param = param
        # self.enabled = False
        # self.daemon = True
        # self.p = pyaudio.PyAudio()
        # self.stream = self.p.open(format=pyaudio.paInt16,
                                  # channels=param['channels'],
                                  # rate=param['rate'],
                                  # frames_per_buffer=param['frames_per_buffer'],
                                  # input=True,
                                  # output=True)

        # if client_mode:
            # self.ctos = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.stoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # self.ctos.bind(('', param['kand_port'] ))
        # else:
            # self.ctos = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # self.stoc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # self.ctos.bind(('', param['kand_port'] ))
            # #self.stoc.bind(('', str(int(param['kand_port']) + 1) ))

    # def enable(self):
        # self.enabled = True
        
    # def disable(self):
        # self.enabled = False
        
    # def switch(self):
        # if self.enabled:
            # print 'VOICE deactivated'
        # else:
            # print 'VOICE activated'
        # self.enabled = not self.enabled
    
    # def run(self):
        # print 'running'
        # if self.client_mode:
            # print 'client mode'
            # i = 0
            # while True:
                # print 'inner loop'
                # if self.enabled:
                    # print 'enabled'
                    # data = self.stream.read(self.param['frames_per_buffer'])
                    # self.stoc.sendto(data[:1024], (self.addr, self.port))
                    # self.stoc.sendto(data[1024:], (self.addr, self.port))
                    # print 'sent pkt'
                    
                    # data, addr = self.ctos.recvfrom(1024)
                    # print 'recvd pkt'
                    # self.stream.write(data)
                    # print 'output pkt'
                                        
                    # print i, '\r',
                    # i += 1
                    # if i / 100 == 0:
                        # print 'VOICE transmitted', i, 'packets so far'

        # else:
            # i = 0
            # while True:
                # if self.enabled:
                    # data = self.stream.read(self.param['frames_per_buffer'])
                    # self.stoc.sendto(data[:1024], (self.addr, self.port))
                    # self.stoc.sendto(data[1024:], (self.addr, self.port))
                    # print 'sent pkt'
                    
                    # data, addr = self.stoc.recvfrom(1024)
                    # print 'recvd pkt'
                    # self.stream.write(data)
                    # print 'output pkt'
                    
                    # print i, '\r',
                    # i += 1
                    # if i / 100 == 0:
                        # print 'VOICE transmitted', i, 'packets so far'


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
