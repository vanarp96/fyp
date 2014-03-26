__author__ = 'viren'

import Crypto.Cipher.AES as AES
import Crypto.Random.OSRNG as OSRNG


# use AES 256 by default
class Cry:
    def __init__(self, block_size=16, key_size=32):
        self.block_size = block_size
        self.key_size = key_size
        self.init_vector = self.gen_init_vector(block_size)
        self.key = self.gen_key(32)

    def pad(self, data):
        if len(data) % self.block_size == 0:
            return data
        pad_len = 15 - (len(data) % self.block_size)
        data = '%s\x80' % data
        return '%s%s' % (data, '\x00' * pad_len)

    def unpad(self, data):
        if not data:
            return data
        data = data.rstrip('\x00')
        if data[-1] == '\x80':
            return data[:-1]
        else:
            return data

    def encrypt(self, data):
        aes = AES.new(self.key, AES.MODE_CBC, self.init_vector)
        return aes.encrypt(self.pad(data))

    def decrypt(self, data):
        aes = AES.new(self.key, AES.MODE_CBC, self.init_vector)
        return self.unpad(aes.decrypt(data))

    @staticmethod
    def gen_init_vector(block_size=16):
        return OSRNG.posix.new().read(block_size)

    @staticmethod
    def gen_key(key_size=32):
        return OSRNG.posix.new().read(key_size)
