#!/usr/bin/env python
# coding:utf-8

""" video process manager """

import os
import signal
import threading
import subprocess
from logger import APPLOGGER
from videocmd import RaspvidCmd

class Singleton(type):
    """ Singleton """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                    super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class VideoProcessMng(object):
    """ VideoProcessMng ensure one video process in thread """
    __metaclass__ = Singleton
    def __init__(self):
        self.vvprocess = None
        self.__process_lock = threading.Lock()
        self.process_cmd = RaspvidCmd()
    def getlock(self):
        """ get lock """
        self.__process_lock.acquire()
    def releaselock(self):
        """ release lock """
        self.__process_lock.release()
    def setprocess(self, process):
        """ set process """
        self.vvprocess = process
    def isset(self):
        """ is set or not """
        if self.vvprocess is not None:
            return True
        return False
    def isrun(self):
        """ is run or not """
        if self.vvprocess is not None and self.vvprocess.poll() is None:
            return True
        return False
    def currpid(self):
        """ return pid """
        return self.vvprocess.pid
    def start(self):
        """ start video process """
        APPLOGGER.info('subcall in porcess')
        child = None
        child = subprocess.Popen(self.process_cmd.cmd(),
                                 shell=True, preexec_fn=os.setsid)
        if child is not None:
            self.vvprocess = child
            APPLOGGER.info('video process start and set')
    def stop(self):
        """ kill video process """
        if self.isset() and self.isrun():
            os.killpg(self.vvprocess.pid, signal.SIGTERM)
            APPLOGGER.info('send video process stoped signal')

if __name__ == '__main__':
    PROCESSMNG = VideoProcessMng()
    PROCESSMNG.getlock()
    PROCESSMNG.start()
    PROCESSMNG.releaselock()

    PROCESSMNG.getlock()
    PROCESSMNG.stop()
    PROCESSMNG.releaselock()

