#!/usr/bin/env python
# coding:utf-8
# author TL
""" ctl server for Raspberry Pi vlc stream cam DEMO VERSION! """

import os
import sys
import signal
import threading
from raspiserver.utils import AppException
from raspiserver.utils import get_local_ip
from raspiserver.utils import ConfigReader
from raspiserver.logger import APPLOGGER
from raspiserver.tcpserver import tcpserve
from raspiserver.httpserver import httpserve
from raspiserver.processmng import VideoProcessMng
from raspiserver.recordmng import RecordMng
from raspiserver.fakevod import vodserve

def signal_handler(signals, frame):
    """ handle ctrl -c """
    _, _ = signals, frame
    if PROCESSMNG == None:
        APPLOGGER.info('Process control object is None')
        return
    APPLOGGER.info('server exiting..')
    PROCESSMNG.getlock()
    try:
        if PROCESSMNG.isset():
            if PROCESSMNG.isrun():
                os.killpg(PROCESSMNG.currpid(), signal.SIGTERM)
    finally:
        PROCESSMNG.releaselock()

    APPLOGGER.info('shutdown complete')
    sys.exit(0)

class HybirdServer(object):
    """ HybirdServer """
    def __init__(self):
        self.__callbacklistdict = {}
        self.thrlist = []
    def setservices(self, name, callback, params):
        """ set services and params """
        self.__callbacklistdict[name] = [callback, params]
    def __preserve(self):
        """ preserve """
        self.thrlist = []
        for name in self.__callbacklistdict.keys():
            cbinfo = self.__callbacklistdict[name]
            # quick and dirty
            tmpthr = threading.Thread(target=cbinfo[0], args=cbinfo[1])
            tmpthr.setDaemon(True)
            tmpthr.setName(name)
            self.thrlist.append(tmpthr)
    def serve(self):
        """ serve all """
        self.__preserve()
        for item in self.thrlist:
            item.start()
        # none block join ?
        while 1:
            for item in self.thrlist:
                if item is not None and item.isAlive():
                    item.join(1)

def main():
    """ serve for all """
    config_path = './config/raspicam.cfg'
    cfg_parser = ConfigReader(config_path)
    cfg = cfg_parser.parser()
    recmng = RecordMng(cfg.record)
    vvpmng = VideoProcessMng(cfg.video)
    global PROCESSMNG
    PROCESSMNG = vvpmng
    hyserve = HybirdServer()
    # you can start tcp server or http server
    try:
        local_ip = get_local_ip()
        tcpctl_port = cfg.comm_port.tcp_port \
                if cfg.comm_port.tcp_port != 0 else 9999
        http_port = cfg.comm_port.http_port \
                if cfg.comm_port.http_port != 0 else 8080
        vod_port = cfg.comm_port.vod_port \
                if cfg.comm_port.vod_port != 0 else 9001
        if local_ip == '':
            raise AppException('local ip is empty')
        hyserve.setservices('httpserver', httpserve, \
                (local_ip, http_port, cfg, recmng, vvpmng))
        hyserve.setservices('tcpserver', tcpserve, \
                (local_ip, tcpctl_port, cfg, recmng, vvpmng))
        hyserve.setservices('vodserver', vodserve, \
                (local_ip, vod_port))
        hyserve.serve()
    except AppException as ex:
        APPLOGGER.error(ex)

if __name__ == '__main__':
    PROCESSMNG = None
    signal.signal(signal.SIGINT, signal_handler)
    main()
