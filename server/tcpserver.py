#!/usr/bin/env python
# coding:utf-8

""" tcp server for control Rpi video process """

import os
import sys
import time
import socket
import threading
import SocketServer
from logger import APPLOGGER
from utils import AppException
from utils import get_local_ip
from processmng import VideoProcessMng

class TcpCtlServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """ TCPServer """
    allow_reuse_address = True


class TcpCtlHandler(SocketServer.BaseRequestHandler):
    """ TCPServer RequestHandler """
    def __init__(self, request, client_address, server):
        self.maxbuf = 2048
        self.vvpmng = VideoProcessMng()
        self.clientcmd_start = 'start'
        self.clientcmd_stop = 'stop'
        SocketServer.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)

    def handle(self):
        APPLOGGER.info('theading number is ' + str(threading.activeCount()))
        data = self.request.recv(self.maxbuf)
        self.__process_req(data)

    def __start_process(self):
        """ start video process """
        self.vvpmng.getlock()
        try:
            self.vvpmng.process_cmd.record = False
            self.vvpmng.process_cmd.recordfname = ''
            if not self.vvpmng.isset():
                self.vvpmng.start()
                self.request.sendall(self.vvpmng.process_cmd.cmd())
                APPLOGGER.info('video server run.')
            else:
                if self.vvpmng.isrun():
                    APPLOGGER.info('already run subprocess: ' +
                                   str(self.vvpmng.currpid()))
                    APPLOGGER.info('video process already run.')
                    self.request.sendall(self.clientcmd_start + '|' + '1')
                    self.request.sendall(self.vvpmng.process_cmd.cmd())
                else:
                    APPLOGGER.info('subprocess not running')
            APPLOGGER.info('activeCount is ' + str(threading.activeCount()))
        finally:
            self.vvpmng.releaselock()

    def __stop_process(self):
        """ __stop_process """
        self.vvpmng.getlock()
        try:
            if not self.vvpmng.isset():
                APPLOGGER.warn('no process to stop')
                self.request.sendall(self.clientcmd_stop + '|' + '0')
                return #just jump to finally
            if self.vvpmng.isrun():
                self.vvpmng.stop()
                APPLOGGER.warn('terminating..')
                self.vvpmng.setprocess(None)
                # fake done
                self.request.sendall(self.clientcmd_stop + '|' + '1')
            else:
                APPLOGGER.info('process is terminate')
                self.vvpmng.setprocess(None)
                self.request.sendall(self.clientcmd_stop + '|' + '0')
        finally:
            self.vvpmng.releaselock()

    def __sysinfo(self):
        """ for get cmd """
        ipaddr, _ = self.server.server_address
        vport = self.vvpmng.process_cmd.rtsp_port
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
            self.vvpmng.process_cmd.bright = int(paradict['brightness'])
        if 'bitrate' in paradict:
            self.vvpmng.process_cmd.bitrate = int(paradict['bitrate'])
        if 'fps' in paradict:
            self.vvpmng.process_cmd.fps = int(paradict['fps'])
        if 'height' in paradict:
            self.vvpmng.process_cmd.height = int(paradict['height'])
        if 'width' in paradict:
            self.vvpmng.process_cmd.width = int(paradict['width'])

        self.vvpmng.getlock()
        try:
            if not self.vvpmng.isset():
                self.vvpmng.start()
                return
            if self.vvpmng.isrun():
                self.vvpmng.stop()
                self.vvpmng.setprocess(None)
                self.vvpmng.start()
            else:
                self.vvpmng.start()
        finally:
            self.vvpmng.releaselock()

    def __record(self):
        recdir = '/home/pi/records'
        currtime = time.gmtime()
        rec_sub_dir_name = ''
        rec_sub_dir_name += str(currtime.tm_year) + '_'
        rec_sub_dir_name += str(currtime.tm_mon) + '_'
        rec_sub_dir_name += str(currtime.tm_mday)
        day_recdir = recdir + '/' + rec_sub_dir_name
        filename = str(currtime.tm_hour) + ':' + \
                   str(currtime.tm_min) + ':' + \
                   str(currtime.tm_sec)
        whole_fname = day_recdir + '/' + filename
        if os.path.exists(day_recdir):
            if os.path.isdir(day_recdir):
                if os.path.exists(whole_fname):
                    os.remove(whole_fname)
            else:
                os.remove(day_recdir)
                os.makedirs(day_recdir)
        else:
            os.makedirs(day_recdir)

        self.vvpmng.getlock()
        self.vvpmng.process_cmd.record = True
        self.vvpmng.process_cmd.recordfname = whole_fname
        APPLOGGER.debug(self.vvpmng.process_cmd.cmd())
        try:
            if not self.vvpmng.isset():
                self.vvpmng.start()
                return
            if self.vvpmng.isrun():
                self.vvpmng.stop()
                self.vvpmng.setprocess(None)
                self.vvpmng.start()
            else:
                self.vvpmng.start()
        finally:
            self.request.sendall(self.vvpmng.process_cmd.cmd())
            self.vvpmng.releaselock()


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
        elif data.lower() == 'record':
            self.__record()
        else:
            APPLOGGER.info('Cmd not support: ' + data)


def tcpserve(ipaddr, serve_port):
    """ tcpserve """
    try:
        if ipaddr is '':
            raise AppException('get local ip exp')
        if int(serve_port) <= 0 or int(serve_port) > 65535:
            raise AppException('port num err')
    except AppException as ex:
        APPLOGGER.error(ex)

    host, port = ipaddr, int(serve_port)
    server = None
    try:
        server = TcpCtlServer((host, port), TcpCtlHandler)
    except socket.error as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    APPLOGGER.info('Server Up IP=%s PORT=%s', ipaddr, serve_port)
    if server:
        server.serve_forever()
    else:
        raise AppException('server start err')


if __name__ == '__main__':
    SERVER, PORT = get_local_ip(), 9999
    tcpserve(SERVER, PORT)
