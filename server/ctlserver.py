#!/usr/bin/env python
# coding:utf-8
# author TL
""" ctl server for Raspberry Pi vlc stream cam DEMO VERSION! """

import os
import sys
import signal
import socket
import threading
import netifaces
import SocketServer
import logging
import subprocess


def signal_handler(signals, frame):
    """ handle ctrl -c """
    _, _ = signals, frame
    APPLOGGER.info('server exiting..')
    ThreadedTCPRequestHandler.process_lock.acquire()
    try:
        if ThreadedTCPRequestHandler.vvprocess is not None:
            if ThreadedTCPRequestHandler.vvprocess.poll() is None:
                os.killpg(ThreadedTCPRequestHandler.vvprocess.pid,
                          signal.SIGTERM)
    finally:
        ThreadedTCPRequestHandler.process_lock.release()

    APPLOGGER.info('shutdown complete')
    sys.exit(0)

def loggerinit():
    """ init logger """
    fstr = '%(asctime)s %(levelname)-8s %(funcName)s %(lineno)s %(message)s'
    fomatter = logging.Formatter(fstr)
    _logger = logging.getLogger('ctl_logger')
    _logger.setLevel(logging.DEBUG)
    shandler = logging.StreamHandler()
    fhandler = logging.FileHandler('/home/pi/ctlserver.log')
    shandler.setFormatter(fomatter)
    fhandler.setFormatter(fomatter)
    _logger.addHandler(shandler)
    _logger.addHandler(fhandler)
    return _logger

APPLOGGER = loggerinit()
APPLOGGER.setLevel('INFO')

class AppException(Exception):
    """ AppException """
    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

    def __str__(self):
        return repr(self.value)

class RaspvidCmd(object):
    """ opt the cmd str """
    def __init__(self):
        self.fps = 30
        self.bright = 50       # 0 - 100
        self.bitrate = 4500000 # 4.5MBit/s
        self.rtsp_port = 9000
        self.width = 1280
        self.height = 720
        self.stime = 0         # forever

    def cmd(self):
        """ return cmd str """
        raspvidbase = "raspivid"
        vlcbase = "cvlc"
        cmdstr = ''
        cmdstr += raspvidbase + ' '
        cmdstr += '-br ' + str(self.bright) + ' '
        cmdstr += '-w ' + str(self.width) + ' '
        cmdstr += '-h ' + str(self.height) + ' '
        cmdstr += '-b '  + str(self.bitrate) + ' '
        cmdstr += '-fps ' + str(self.fps) + ' '
        cmdstr += '-vf -hf' + ' '
        cmdstr += '-t ' + str(self.stime) + ' '
        cmdstr += '-o -' + ' '

        cmdstr += '|' + ' '
        cmdstr += vlcbase + ' '
        cmdstr += "-vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:"
        cmdstr += str(self.rtsp_port) + "/}' :demux=h264"
        return cmdstr

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    """ TCPServer RequestHandler """
    vvprocess = None
    process_lock = threading.Lock()
    def __init__(self, request, client_address, server):
        self.maxbuf = 2048
        self.maxthr = 4
        self.raspcmd = RaspvidCmd()
        self.clientcmd_start = "start"
        self.clientcmd_stop = "stop"
        SocketServer.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)

    def handle(self):
        if threading.activeCount() > self.maxthr:
            APPLOGGER.warn('theading number exceeded')
            return
        data = self.request.recv(self.maxbuf)
        self.__process_req(data)

    def __start_process(self):
        """ start video process """
        ThreadedTCPRequestHandler.process_lock.acquire()
        try:
            if ThreadedTCPRequestHandler.vvprocess is None:
                self.__sub_call(self.raspcmd.cmd())
                self.request.sendall(self.raspcmd.cmd())
                APPLOGGER.info("video server run.")
            else:
                if ThreadedTCPRequestHandler.vvprocess.poll() is None:
                    APPLOGGER.info('already run subprocess: ' +
                                   str(ThreadedTCPRequestHandler.vvprocess.pid))
                    APPLOGGER.info("video process already run.")
                    self.request.sendall(self.clientcmd_start + '|' + '1')
                    self.request.sendall(self.raspcmd.cmd())
                else:
                    APPLOGGER.info('subprocess not running')
            APPLOGGER.info('activeCount is ' + str(threading.activeCount()))
        finally:
            ThreadedTCPRequestHandler.process_lock.release()

    def __stop_process(self):
        """ __stop_process """
        ThreadedTCPRequestHandler.process_lock.acquire()
        try:
            if ThreadedTCPRequestHandler.vvprocess is None:
                APPLOGGER.warn('no process to stop')
                self.request.sendall(self.clientcmd_stop + '|' + '0')
                return
            if ThreadedTCPRequestHandler.vvprocess.poll() is None:
                os.killpg(ThreadedTCPRequestHandler.vvprocess.pid,
                          signal.SIGTERM)
                # ThreadedTCPRequestHandler.vvprocess.terminate()
                APPLOGGER.warn('terminating..')
                ThreadedTCPRequestHandler.vvprocess = None
                self.request.sendall(self.clientcmd_stop + '|' + '1') # fake done
            else:
                APPLOGGER.info('process is terminate')
                ThreadedTCPRequestHandler.vvprocess = None
                self.request.sendall(self.clientcmd_stop + '|' + '0')
        finally:
            ThreadedTCPRequestHandler.process_lock.release()

    def __sysinfo(self):
        """ for get cmd """
        ipaddr, _ = self.server.server_address
        vport = self.raspcmd.rtsp_port
        self.request.sendall(str(ipaddr) + ':' + str(vport))

    def __changevprocss(self, data):
        """ change video process paramters
            change|cmd1=opt, cmd2=opt2, ... """
        data = data.lstrip('change|')
        data = data.split(',')
        APPLOGGER.debug(data)
        paradict = {}
        try:
            paradict = dict([item.split('=') for item in data if item != ''])
            if not paradict:
                raise AppException('paradict dict is empty')
        except AppException as ex:
            APPLOGGER.error(ex)
            return

        if 'brightness' in paradict:
            self.raspcmd.bright = int(paradict['brightness'])
        if 'bitrate' in paradict:
            self.raspcmd.bitrate = int(paradict['bitrate'])
        if 'fps' in paradict:
            self.raspcmd.fps = int(paradict['fps'])
        if 'height' in paradict:
            self.raspcmd.height = int(paradict['height'])
        if 'width' in paradict:
            self.raspcmd.width = int(paradict['width'])

        ThreadedTCPRequestHandler.process_lock.acquire()
        try:
            if ThreadedTCPRequestHandler.vvprocess is None:
                self.__sub_call(self.raspcmd.cmd())
                return
            if ThreadedTCPRequestHandler.vvprocess.poll() is None:
                os.killpg(ThreadedTCPRequestHandler.vvprocess.pid,
                          signal.SIGTERM)
                ThreadedTCPRequestHandler.vvprocess = None
                self.__sub_call(self.raspcmd.cmd())
            else:
                self.__sub_call(self.raspcmd.cmd())
        finally:
            ThreadedTCPRequestHandler.process_lock.release()

    def __process_req(self, data):
        """ process req """
        data = data.strip(' \n')
        if len(data) <= 0:
            return
        if data.lower() == 'start':
            self.__start_process()
        elif data.lower() == 'stop':
            self.__stop_process()
        elif data.lower() == 'get':
            self.__sysinfo()
        elif data.lower().startswith('change'):
            self.__changevprocss(data)
        else:
            APPLOGGER.info('Cmd not support: ' + data)

    @classmethod
    def __sub_call(cls, cmdstr):
        """ sub_call for vv stream """
        APPLOGGER.info('subcall in porcess')
        child = None
        child = subprocess.Popen(cmdstr, shell=True, preexec_fn=os.setsid)
        if child is not None:
            cls.vvprocess = child

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """ TCPServer """
    pass


def __get_local_ip():
    """ get local ip address """
    ipaddr = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    return ipaddr

def tcpserve():
    """ tcpserve """
    ipaddr = ''
    try:
        ipaddr = __get_local_ip()
        if ipaddr is '':
            raise AppException('get local ip exp')
    except AppException as ex:
        APPLOGGER.error(ex)

    host, port = ipaddr, 9999
    server = None
    try:
        server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
    except socket.error as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    APPLOGGER.info('Server Up')
    if server:
        server.serve_forever()
    else:
        raise AppException('server start err')

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    tcpserve()
