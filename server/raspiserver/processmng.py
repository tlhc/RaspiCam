#!/usr/bin/env python
# coding:utf-8
# author TL

""" video process manager """

import os
import signal
import threading
import subprocess
from raspiserver.logger import APPLOGGER
from raspiserver.videocmd import RaspvidCmd
from raspiserver.utils import Singleton

class VideoProcessMng(object):
    """ VideoProcessMng ensure one video process in thread """
    __metaclass__ = Singleton
    def __init__(self, cfg):
        self.__vvprocess = None
        self.__process_lock = threading.Lock()
        self.process_cmd = RaspvidCmd(cfg)
    def getlock(self):
        """ get lock """
        self.__process_lock.acquire()
    def releaselock(self):
        """ release lock """
        self.__process_lock.release()
    def setprocess(self, process):
        """ set process """
        self.__vvprocess = process
    def isset(self):
        """ is set or not """
        if self.__vvprocess is not None:
            return True
        return False
    def isrun(self):
        """ is run or not """
        if self.__vvprocess is not None and self.__vvprocess.poll() is None:
            return True
        return False
    def currpid(self):
        """ return pid """
        return self.__vvprocess.pid
    def start(self):
        """ start video process """
        APPLOGGER.info('subcall in porcess')
        child = None
        child = subprocess.Popen(self.process_cmd.cmd(),
                                 shell=True, preexec_fn=os.setsid)
        if child is not None:
            self.__vvprocess = child
            APPLOGGER.info('video process start and set')
    def stop(self):
        """ kill video process """
        if self.isset() and self.isrun():
            os.killpg(self.__vvprocess.pid, signal.SIGTERM)
            APPLOGGER.info('send video process stoped signal')
