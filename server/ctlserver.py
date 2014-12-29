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
from raspiserver.fakevod import vodserve
from raspiserver.processmng import VideoProcessMng
from raspiserver.recordmng import RecordMng

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
    config_path = '/home/pi/server/config/raspicam.cfg'
    cfg_parser = ConfigReader(config_path)
    cfg = cfg_parser.parser()
    recmng = RecordMng(cfg.record)
    vvpmng = VideoProcessMng(cfg.video)
    global PROCESSMNG
    PROCESSMNG = vvpmng
    hyserve = HybirdServer()
    # you can start tcp server or http server
    try:
        hyserve.setservices('httpserver', httpserve, (cfg, recmng, vvpmng))
        hyserve.setservices('tcpserver', tcpserve, (cfg, recmng, vvpmng))
        hyserve.setservices('vodserver', vodserve, (cfg,))
        hyserve.serve()
    except AppException as ex:
        APPLOGGER.error(ex)

if __name__ == '__main__':
    PROCESSMNG = None
    signal.signal(signal.SIGINT, signal_handler)
    main()
