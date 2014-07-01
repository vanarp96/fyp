#!/usr/bin/env python
__author__ = 'INSPIRON14R'

import sys
# import socket
# import threading
import pickle
import select
import struct
import logging
import getopt
# import Queue
import SocketServer
from datetime import datetime
from bidict import bidict
from comm import *
from config import *
from cry import *
from gui import *

global udpservers, udpserverslock, client, localaddress, serveraddress, port, remotefwdto, udpports, tcpconnections, \
    tcpconnsock2key, udpportnat

udpserverslock = threading.Lock()

udpservers = dict()
tcpconnections = dict()
tcpconnsock2key = dict()
udpportnat = bidict()


def usage():
    print sys.argv[0], '[OPTION]...'
    print 'Runs as server when no arguments are given'
    print '-c, --client  run as client'
    print '-h, --help    display this help & exit'
    sys.exit()

console_lock = threading.Lock()
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
config_reader = Config()
config_dict = config_reader.readall()
creeper = Cry(config_dict['key'], config_dict['init_vector'])


def log(*args):
    if not config_dict['logging']:
        return
    with console_lock:
        logging.info(''.join([str(x) for x in args]))


def clientsendpktcallback(client_address, server_address, sendingto, udp):
    global udpserverslock
    rport = server_address[1]
    sport = client_address[1]

    dst = (sendingto, rport)
    f = (('0.0.0.0', udpportnat[:sport]))
    log("(UDP) forwarding packet from ", f, " to ", dst)

    try:
        with udpserverslock:
            udpservers[f].socket.sendto(udp, dst)
    except KeyError:
        log(udpservers.items())


def serversendpktcallback(client_address, server_address, sendingto, udp):
    global udpserverslock
    rport = server_address[1]
    sport = client_address[1]

    dst = (sendingto, rport)
    f = (('0.0.0.0', udpportnat[:sport]))
    log("(UDP) forwarding packet from ", f, " to ", dst)

    try:
        with udpserverslock:
            udpservers[client_address].socket.sendto(udp, dst)
    except KeyError:
        log(udpservers.values())
        raise


class TCPConnection(object):
    def __init__(self, tcp_socket, tcp_socket_lock, src):
        self.tcp_socket = tcp_socket
        self.tcp_socket_lock = tcp_socket_lock
        self.src = src
        self.bf = ''


class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    last_received = datetime.now()

    def set_client_mode(self):
        self.clientmode = True

    def set_tcp_socket(self, tcp_socket, tcp_socket_lock):
        self.tcp_socket = tcp_socket
        self.tcp_socket_lock = tcp_socket_lock


class ThreadedUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.server.lastreceived = datetime.now()

        src = [x for x in self.client_address]
        dst = [x for x in self.server.server_address]

        log("(UDP)(not NATed) received from ", src, " for ", self.server.server_address)

        if not (getattr(self.server, 'clientmode', None)):
            rport = dst[1]
            log("(UDP) port translated from ", dst, ' to ', udpportnat[rport:])
            rport = udpportnat[rport:]
            dst[1] = rport

        # payload to be sent is in 'self.request[0]'
        if config_dict['encryption']:
            print 'encrypt'
            s = pickle.dumps((tuple(src), tuple(dst), creeper.encrypt(self.request[0]),), pickle.HIGHEST_PROTOCOL)
        else:
            s = pickle.dumps((tuple(src), tuple(dst), self.request[0],), pickle.HIGHEST_PROTOCOL)

        if getattr(self.server, 'clientmode', False):
            # tcpc = None
            key = tuple(map(None, src, (dst[1],)))

            if not tcpconnections.has_key(key):
                tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                log("(TCP) connecting to ", serveraddress, ":", port, " to forward from ", src, " to ",
                    (remotefwdto, dst[1]))
                tcp_socket.connect((serveraddress, port))
                tcp_socket_lock = threading.Lock()

                tcpconnections[key] = TCPConnection(tcp_socket, tcp_socket_lock, src)
                tcpconnsock2key[tcp_socket] = key

                b = "%s\n%s" % (self.client_address, remotefwdto)
                b += ' ' * (128 - len(b)) if len(b) < 128 else ''
                tcp_socket.send(b)
                self.server.set_tcp_socket(tcp_socket, tcp_socket_lock)

        log("(TCP) sending (NATed) UDP from ", src, " to ", dst, " on TCP ")
        self.server.tcp_socket_lock.acquire()
        self.server.tcp_socket.send(struct.pack("!I%ds" % len(s), len(s), s))
        self.server.tcp_socket_lock.release()


def read_tcp(tcp_socket, tcp_socket_lock, bf, sendingto, srvcallback=None, sendpktcallback=None):
    r = None
    tcp_socket_lock.acquire()
    tcp_socket.settimeout(0.1)
    try:
        readin = tcp_socket.recv(4096)
        if len(readin) == 0:
            raise socket.error
        bf += readin
        if len(bf) > 4:
            msglen = struct.unpack('!I', bf[:4])[0]
            if len(bf) >= msglen + 4:
                (msglen, msg) = struct.unpack("!I%ds" % msglen, bf[:msglen + 4])
                # bf = bf[struct.calcsize("!I%ds" % msglen):]
                (client_address, server_address, udp) = pickle.loads(msg)
                if config_dict['encryption']:
                    udp = creeper.decrypt(udp)

                log("(TCP) received UDP from ", client_address, " addressed to ", server_address)

                if srvcallback is not None:
                    r = srvcallback(client_address, sendingto, tcp_socket, tcp_socket_lock)

                if sendpktcallback is not None:
                    sendpktcallback(client_address, server_address, sendingto, udp)

    except socket.timeout:
        log("Socket read timed out for ", tcp_socket)
    finally:
        tcp_socket_lock.release()
    return r


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    def __init__(self, server_address, request_handler_class, bind_and_activate=True):
        SocketServer.TCPServer.allow_reuse_address = True
        SocketServer.TCPServer.__init__(self, server_address, request_handler_class, bind_and_activate)


class ThreadedTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        def start_udp_server(claddress, sendingto, tcp_socket, tcp_socket_lock):
            rport = claddress[1]
            with udpserverslock:
                if not udpservers.has_key(claddress):
                    log("(TCP) started UDP server for ", claddress)
                    udpservers[claddress] = ThreadedUDPServer(('0.0.0.0', 0), ThreadedUDPHandler)
                    udpportnat[:rport] = udpservers[claddress].socket.getsockname()[1]
                    udpportnat[udpservers[claddress].socket.getsockname()[1]:] = rport
                    self.server_address = udpservers[claddress].socket.getsockname()

                    log("(TCP) bound incoming port ", rport, " as NAT ", (sendingto, udpportnat[:rport]))
                    udpservers[claddress].set_tcp_socket(tcp_socket, tcp_socket_lock)
                    server_thread = threading.Thread(target=udpservers[claddress].serve_forever)
                    server_thread.setDaemon(True)
                    server_thread.start()

                    return (claddress, udpservers[claddress])
                else:
                    return None

        # fwdto = None
        # fa = None
        udps = []

        nb = ''
        while len(nb) < 128:
            fwdto = self.request.recv(128)
            if len(fwdto) == 0:
                raise socket.error
            nb += fwdto
        src, nm = [x.lstrip().rstrip() for x in nb[:128].split('\n')]
        sendingto = "127.0.0.1"
        log("(TCP) started server forwarding to ", nm, " as ", sendingto, " for other source ", src)
        # nb = nm[128:]

        bf = ''
        try:
            while True:
                (rs, ws, ex) = select.select([self.request], [], [])
                r = read_tcp(self.request, threading.Lock(), bf, sendingto, start_udp_server, serversendpktcallback)
                if r is not None:
                    udps.append(r)
        except (socket.error,), e:
            log(e)
            self.request.close()

        with udpserverslock:
            log("(TCP) server for ", nm, " with source ", src, " stopping ", len(udps), " UDP server(s)")
            for u in udps:
                u[1].shutdown()
                del udpservers[u[0]]
            log("(TCP) shutting down server forwarding for ", nm, " as ", sendingto, " other source ", src)


########################################################################################################################
########################################################################################################################

if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hcs", ["help", "client"])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit()

    client = False
    for o, a in opts:
        if o in ('-c', '--client'):
            client = True
        elif o in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            assert False, "unhandled option"

    localaddress = config_dict['clientaddr']
    serveraddress = config_dict['serveraddr']
    remotefwdto = config_dict['destaddr']
    firstport = None
    port = config_dict['destport']
    udpports = config_dict['clientport']

    if client:
        log("Running as client")
        if config_dict['mode'] == 1:
            th = Text(True, config_dict)
            th.start()
        elif config_dict['mode'] == 2:
            th = Voice(True, config_dict)
            th.start()
        else:
            th = FileAudio(True, config_dict)
            th.start()
            
        if config_dict['do_kand']:
            print 'doing kand'
            kand = Kand(True, config_dict)
            kand.start()
            
        if config_dict['gui']:
            g = GUI(th, kand)
            g.start()

        for rport in udpports:
            with udpserverslock:
                udpservers[(localaddress, rport)] = ThreadedUDPServer((localaddress, rport), ThreadedUDPHandler)
                udpservers[(localaddress, rport)].set_client_mode()
                udpportnat[rport:] = rport
                udpportnat[:rport] = rport
                server_thread = threading.Thread(target=udpservers[(localaddress, rport)].serve_forever)
                server_thread.setDaemon(True)
                server_thread.start()

        while True:
            rs = [k.tcp_socket for k in tcpconnections.values() if k.tcp_socket is not None]
            ws = None
            ex = None
            (rs, ws, ex) = select.select(rs, [], [], 10)
            for v in rs:
                try:
                    try:
                        o = tcpconnections[tcpconnsock2key[v]]
                    except KeyError:
                        log(tcpconnections.items())
                        raise
                    assert o.tcp_socket == v
                    read_tcp(o.tcp_socket, o.tcp_socket_lock, o.bf, o.src[0], None, clientsendpktcallback)

                except socket.error, e:
                    log("(TCP) client connection for ", o.src, " was closed")
                    del tcpconnections[tcpconnsock2key[o.tcp_socket]]
                    del tcpconnsock2key[o.tcp_socket]
                    o.tcp_socket.close()
                    del o

    else:
        if config_dict['do_kand']:
            #print 'doing kand'
            kand = Kand(False, config_dict)
            kand.start()
        if config_dict['mode'] == 0:
            th = FileAudio(False, config_dict)
        elif config_dict['mode'] == 1:
            th = Text(False, config_dict)
        elif config_dict['mode'] == 2:
            th = Voice(False, config_dict)
        else:
            log('config file error')
            sys.exit()
        th.start()
        
        if config_dict['gui']:
            g = GUI(th, kand)
            g.start()

        log("Running as server")
        server = ThreadedTCPServer(('', port), ThreadedTCPHandler)
        server.serve_forever()
