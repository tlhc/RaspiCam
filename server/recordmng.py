#!/usr/bin/env python
# coding:utf-8

""" record manager """
from os import listdir
from os import statvfs, remove, makedirs
from os.path import isdir, join, isfile, exists, getctime, getsize
from logger import APPLOGGER
from time import gmtime
from utils import Singleton
from utils import AppException

class RecordMng(object):
    """ record video file manager """
    __metaclass__ = Singleton
    def __init__(self, record_base):
        self.__recordbase = record_base
        self.lefthrhold = 100    #threshhold disk space for record in MB
        self.cycle = False
        APPLOGGER.debug(record_base)

    def get_recordfiles(self):
        """ get all record files """
        dirs = [item for item in listdir(self.__recordbase) \
                if isdir(join(self.__recordbase, item))]
        day_dir = [join(self.__recordbase, item) for item in dirs]
        allfiles = []
        for rec_dir in day_dir:
            files = [join(rec_dir, item) for item in listdir(rec_dir) \
                     if isfile(join(rec_dir, item))]
            allfiles.extend(files)
        return allfiles

    def get_freespaces(self):
        """ get the base dir free space in MB """
        vfsinfo = statvfs(self.__recordbase)
        tsize = (vfsinfo.f_bavail * vfsinfo.f_frsize) / 1024
        return tsize / 1024

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
                APPLOGGER.debug('relase space is : ' + str(getfsize(item)))
                remove(item)
            else:
                break
        APPLOGGER.debug('free space is: ' + str(self.get_freespaces()))


    def can_record(self):
        """ can record videos if we have enough disk space just pre check """
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
            if self.can_record():
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

if __name__ == '__main__':
    RECORDMNG = RecordMng('/home/pi/records/')
    ALLFILES = RECORDMNG.get_recordfiles()
    APPLOGGER.debug(ALLFILES)
    APPLOGGER.debug(len(ALLFILES))

    APPLOGGER.debug(RECORDMNG.get_freespaces())
    APPLOGGER.debug(RECORDMNG.can_record())
    RECORDMNG.lefthrhold = 350
    RECORDMNG.cycle = True
    APPLOGGER.debug(RECORDMNG.can_record())
    APPLOGGER.debug(RECORDMNG.gen_recordfname())

