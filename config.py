__author__ = 'INSPIRON14R'

import ConfigParser


class Config:
    def __init__(self):
        self.configfile = 'config.txt'
        self.cp = ConfigParser.ConfigParser()
        self.cp.read(self.configfile)

    def readall(self):
        cfg = dict()

        cfg['logging'] = self.cp.getboolean('general', 'logging')
        a = self.cp.get('general', 'mode')
        if a == 'debug':
            cfg['mode'] = 0
        elif a == 'text':
            # mode 0 = debug (wav trans)
            # mode 1 = text
            # mode 2 = voice
            cfg['mode'] = 1
        elif a == 'voice':
            cfg['mode'] = 2

        cfg['clientaddr'] = self.cp.get('client', 'address')
        cfg['serveraddr'] = self.cp.get('server', 'address')
        cfg['destport'] = self.cp.getint('destination', 'port')
        cfg['destaddr'] = self.cp.get('destination', 'address')
        cfg['clientport'] = [self.cp.getint('client', 'port')]

        cfg['key'] = self.cp.get('crypto', 'key').decode('string_escape')
        cfg['init_vector'] = self.cp.get('crypto', 'init_vector').decode('string_escape')
        # print 'key =', cfg['key'].encode('string_escape')
        # print 'init_vector =', cfg['key'].encode('string_escape')

        cfg['channels'] = self.cp.getint('audio', 'channels')
        cfg['rate'] = self.cp.getint('audio', 'rate')
        cfg['frames_per_buffer'] = self.cp.getint('audio', 'frames_per_buffer')

        return cfg

    def read(self, section, item):
        return self.cp.get(section, item)

    def save(self, section, item, value):
        self.cp.set(section, item, value)
        self.cp.write(open(self.configfile, 'w'))
