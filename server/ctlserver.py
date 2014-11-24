#!/usr/bin/env python
# coding:utf-8
# author TL
""" ctl server for Raspberry Pi vlc stream cam DEMO VERSION! """

import os
import sys
import signal
import threading
from utils import AppException
from utils import get_local_ip
from logger import APPLOGGER
from tcpserver import tcpserve
from httpserver import httpserve
from processmng import VideoProcessMng

def signal_handler(signals, frame):
    """ handle ctrl -c """
    _, _ = signals, frame
    APPLOGGER.info('server exiting..')
    vvpmng = VideoProcessMng()
    vvpmng.getlock()
    try:
        if vvpmng.isset():
            if vvpmng.isrun():
                os.killpg(vvpmng.currpid(), signal.SIGTERM)
    finally:
        vvpmng.releaselock()

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
            _cbinfo = self.__callbacklistdict[name]
            # quick and dirty
            _tmpthr = threading.Thread(target=_cbinfo[0], args=_cbinfo[1])
            _tmpthr.setDaemon(True)
            _tmpthr.setName(name)
            self.thrlist.append(_tmpthr)
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
    hyserve = HybirdServer()
    # you can start tcp server or http server
    try:
        local_ip = get_local_ip()
        tcpctl_port = 9999
        http_port = 8080
        if local_ip == '':
            raise AppException('local ip is empty')
        hyserve.setservices('httpserver', httpserve, (local_ip, http_port))
        hyserve.setservices('tcpserver', tcpserve, (local_ip, tcpctl_port))
        hyserve.serve()
    except AppException as ex:
        APPLOGGER.error(ex)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
