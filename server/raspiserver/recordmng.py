#!/usr/bin/env python
# coding:utf-8
# author TL

""" record manager """

import sys
from os import listdir
from os import statvfs, remove, makedirs
from os.path import isdir, join, isfile, exists, getctime, getsize
from time import gmtime
from time import sleep
from threading import Lock, Thread
from raspiserver.utils import Singleton
from raspiserver.utils import AppException
from raspiserver.logger import APPLOGGER
from raspiserver.fakevod import getvodfile


class RecordMng(object):
    """ record video file manager """
    __metaclass__ = Singleton
    def __init__(self, cfg):
        self.__reclock = Lock()
        self.__recordbase = cfg.base.strip("'") \
                if cfg.base != '' else '/home/pi/records'
        self.lefthrhold = cfg.fsp_limit if cfg.fsp_limit != -1 else 100
        self.cycle = cfg.cycle if cfg.cycle != None else False
        try:
            if not exists(self.__recordbase):
                makedirs(self.__recordbase)
            elif not isdir(self.__recordbase):
                remove(self.__recordbase)
                makedirs(self.__recordbase)
        except OSError as ex:
            APPLOGGER.error(ex)
            APPLOGGER.info('pls use sudo')
            sys.exit(1)
        self.__watchthr = None
        self.__watchthr = Thread(target=self.__watch_dog)
        self.__watchthr.setDaemon(True)
        self.__watchthr.setName('watchthr')
        self.__watchthr.start()
        APPLOGGER.debug(cfg.base)

    def getlock(self):
        """ get lock """
        self.__reclock.acquire()
    def releaselock(self):
        """ release lock """
        self.__reclock.release()

    def get_recordfiles(self):
        """ get all record files """
        allfiles = []
        if exists(self.__recordbase) and isdir(self.__recordbase):
            dirs = [item for item in listdir(self.__recordbase) \
                    if isdir(join(self.__recordbase, item))]
            day_dir = [join(self.__recordbase, item) for item in dirs]

            for rec_dir in day_dir:
                files = [join(rec_dir, item) for item in listdir(rec_dir) \
                         if isfile(join(rec_dir, item))]
                allfiles.extend(files)
        return allfiles

    def get_freespaces(self):
        """ get the base dir free space in MB """
        if exists(self.__recordbase) and isdir(self.__recordbase):
            vfsinfo = statvfs(self.__recordbase)
            tsize = (vfsinfo.f_bavail * vfsinfo.f_frsize) / 1024
            return tsize / 1024
        return 0

    def __free_space(self):
        """ free disk space for record if self.cycle == True """
        rec_files = self.get_recordfiles()
        def filesort(file1, file2):
            """ sort by create time """
            ctime1 = getctime(file1)
            ctime2 = getctime(file2)
            if ctime1 < ctime2:
                return -1
            elif ctime1 == ctime2:
                return 0
            else:
                return 1

        rec_files.sort(cmp=filesort)
        def getfsize(path):
            """ get size for %.3f """
            return float('%.3f' % (getsize(path) / 1024.0 / 1024.0))
        for item in rec_files:
            if self.get_freespaces() < self.lefthrhold:
                APPLOGGER.debug(getvodfile())
                if getvodfile().strip(' ') == item.strip(' '):
                    APPLOGGER.debug('in use: ' + getvodfile())
                    continue
                else:
                    APPLOGGER.debug('relase space is : ' + str(getfsize(item)))
                    remove(item)
            else:
                break
        APPLOGGER.debug('free space is: ' + str(self.get_freespaces()))


    def have_space(self):
        """ can record videos if we have enough disk space
            just pre run record process check """
        if int(self.get_freespaces()) < self.lefthrhold:
            return False
        return True

    def gen_recordfname(self):
        """ generate the video filename """
        currtime = gmtime()
        rec_sub_dir_name = ''
        rec_sub_dir_name += str(currtime.tm_year) + '_'
        rec_sub_dir_name += str(currtime.tm_mon) + '_'
        rec_sub_dir_name += str(currtime.tm_mday)
        day_recdir = self.__recordbase + '/' + rec_sub_dir_name
        filename = str(currtime.tm_hour) + ':' + \
                   str(currtime.tm_min) + ':' + \
                   str(currtime.tm_sec)
        whole_fname = day_recdir + '/' + filename
        try:
            if exists(day_recdir):
                if isdir(day_recdir):
                    if exists(whole_fname):
                        remove(whole_fname)
                else:
                    remove(day_recdir)
                    makedirs(day_recdir)
            else:
                makedirs(day_recdir)
        except OSError as ex:
            APPLOGGER.error(ex)

        # can record but don't have enough space
        try:
            if self.have_space():
                return whole_fname
            else:
                if self.cycle:
                    self.__free_space()
                    return whole_fname
                raise AppException('no space')
        except AppException as ex:
            APPLOGGER.info('free space is: ' + str(self.get_freespaces()))
            APPLOGGER.info('limit is : ' + str(self.lefthrhold))
            APPLOGGER.error(ex)

    def rm_recordfiles(self, rmfpath):
        """ 0  rm success
           -1  can't remove
            1  already remove """
        rec_files = self.get_recordfiles()
        if rmfpath in rec_files:
            try:
                remove(rmfpath)
                return 0
            except OSError:
                pass
            return -1
        return 1

    def __watch_dog(self):
        """ watch the free space """
        freespace = 0
        while 1:
            self.getlock()
            try:
                if not self.have_space() and self.cycle:
                    self.__free_space()
            except OSError:
                pass
            finally:
                freespace = self.get_freespaces()
                self.releaselock()

            APPLOGGER.debug('free space is: ' + \
                    str(freespace) + 'MB')
            sleep(2)


def __test():
    """ test func """
    from raspiserver.utils import ConfigReader
    cfg_parser = ConfigReader('./config/raspicam.cfg')
    cfg = cfg_parser.parser()
    recordmng = RecordMng(cfg.record)
    allfiles = recordmng.get_recordfiles()
    APPLOGGER.debug(allfiles)
    APPLOGGER.debug(len(allfiles))

    APPLOGGER.debug(recordmng.get_freespaces())
    APPLOGGER.debug(recordmng.have_space())
    recordmng.lefthrhold = 330
    recordmng.cycle = True
    APPLOGGER.debug(recordmng.have_space())
    APPLOGGER.debug(recordmng.gen_recordfname())

if __name__ == '__main__':
    __test()

