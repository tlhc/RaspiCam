#!/usr/bin/env python
# coding:utf-8
# author TL

""" tcp server for control Rpi video process """

import sys
import socket
import threading
import SocketServer
from raspiserver.logger import APPLOGGER
from raspiserver.utils import AppException

class TcpCtlServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """ TCPServer """
    def __init__(self, server_address, RequestHandler, cfg, recmng, vvpmng):
        self.allow_reuse_address = True
        # self.cfg = cfg
        self.vod_port = cfg.comm_port.vod_port
        self.vvpmng = vvpmng
        self.recmng = recmng
        SocketServer.TCPServer.__init__(self, server_address, RequestHandler)

class TcpCtlHandler(SocketServer.BaseRequestHandler):
    """ TCPServer RequestHandler """
    def __init__(self, request, client_address, server):
        self.server = server
        self.maxbuf = 2048
        self.vvpmng = self.server.vvpmng
        self.recmng = self.server.recmng
        self.clientcmd_start = 'start'
        self.clientcmd_stop = 'stop'
        self.clientcmd_record = 'record'
        SocketServer.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)
    def handle(self):
        APPLOGGER.debug('theading number is ' + str(threading.activeCount()))
        data = self.request.recv(self.maxbuf)
        self.__process_req(data)

    def __start(self):
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
            self.request.close()
            self.vvpmng.releaselock()

    def __stop(self):
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
            self.vvpmng.process_cmd.record = False
            self.vvpmng.process_cmd.recordfname = ''
            self.request.close()
            self.vvpmng.releaselock()

    def __get(self):
        """ for get cmd """
        ipaddr, _ = self.server.server_address
        vport = self.vvpmng.process_cmd.rtsp_port
        self.request.sendall(str(ipaddr) + ':' + str(vport))
        self.request.close()

    def __change(self, data):
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

        # just change parameter no record here
        self.vvpmng.process_cmd.record = False
        self.vvpmng.process_cmd.recordfname = ''

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
        self.request.sendall(self.vvpmng.process_cmd.cmd())
        self.request.close()

    def __record(self):
        """ record video file """
        recfname = ''
        can_rec = False
        self.recmng.getlock()
        try:
            if self.recmng.have_space() or self.recmng.cycle == True:
                recfname = self.recmng.gen_recordfname()
                if recfname == '':
                    raise AppException('record file name is null')
                can_rec = True
            else:
                raise AppException('no space to record')
        except AppException as ex:
            APPLOGGER.error(ex)
        finally:
            self.recmng.releaselock()

        if not can_rec:
            return

        self.vvpmng.getlock()
        self.vvpmng.process_cmd.record = True
        self.vvpmng.process_cmd.recordfname = recfname
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
            self.vvpmng.releaselock()
        self.request.sendall(self.vvpmng.process_cmd.cmd())
        self.request.close()

    def __get_records(self):
        """ get record files """
        self.recmng.getlock()
        try:
            reclist = self.recmng.get_recordfiles()
        finally:
            msg = 'records|'
            msg += ','.join(reclist)
            self.request.sendall(msg + '\n')
            self.request.close()
            self.recmng.releaselock()

    def __rm_records(self, data):
        """ remove video record """
        data = data.lstrip('rm_records|')
        data = data.strip('\n')
        allfiles = self.recmng.get_recordfiles()
        if data not in allfiles:
            return
        self.recmng.getlock()
        ret = -1
        try:
            ret = self.recmng.rm_recordfiles(data)
        finally:
            if ret == 0 or ret == 1:
                APPLOGGER.info('rm success')
            elif ret == -1:
                APPLOGGER.info('rm failed')
            reclist = self.recmng.get_recordfiles()
            msg = 'records|'
            msg += ','.join(reclist)
            self.request.sendall(msg)
            self.request.close()
            self.recmng.releaselock()

    def __get_vodport(self):
        """ get vod port """
        msg = 'vodport|'
        msg += str(self.server.vod_port)
        self.request.sendall(msg)
        self.request.close()

    def __get_currparams(self):
        """ get curr video param ugly and lazy..."""
        self.request.sendall(self.vvpmng.process_cmd.cmd())
        self.request.close()

    def __process_req(self, data):
        """ process req """
        data = data.strip(' \n')
        if len(data) <= 0:
            return
        callinfo = data.lower()
        callinfo = '__' + callinfo
        callinfo = callinfo.split('|')
        splitlen = len(callinfo)
        if splitlen < 1 or splitlen > 2:
            APPLOGGER.warn('request parameter not correct')
            return
        try:
            callback = getattr(self, '_' + \
                    self.__class__.__name__ + callinfo[0])
            if callback != None and callable(callback):
                if splitlen == 1:
                    callback()
                else:
                    callback(data)
            else:
                APPLOGGER.error('request callback error')
        except AttributeError as ex:
            APPLOGGER.error(ex)

def tcpserve(cfg, recmng, vvpmng):
    """ tcpserve """
    ipaddr = cfg.comm_port.address
    serve_port = cfg.comm_port.tcp_port
    try:
        if ipaddr is '':
            raise AppException('get local ip exp')
        if int(serve_port) <= 0 or int(serve_port) > 65535:
            raise AppException('port num err')
    except AppException as ex:
        APPLOGGER.error(ex)
        sys.exit(1)

    host, port = ipaddr, int(serve_port)
    server = None
    try:
        server = TcpCtlServer((host, port), TcpCtlHandler, cfg, recmng, vvpmng)
    except socket.error as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    APPLOGGER.info('Server Up IP=%s PORT=%s', ipaddr, serve_port)
    if server:
        server.serve_forever()
    else:
        raise AppException('server start err')

def __run():
    """ test function """
    from raspiserver.recordmng import RecordMng
    from raspiserver.utils import ConfigReader
    from raspiserver.processmng import VideoProcessMng
    config_path = './config/raspicam.cfg'
    cfg_parser = ConfigReader(config_path)
    cfg = cfg_parser.parser()
    recmng = RecordMng(cfg.record)
    vvpmng = VideoProcessMng(cfg.video)
    tcpserve(cfg, recmng, vvpmng)

if __name__ == '__main__':
    __run()
