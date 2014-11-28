#!/usr/bin/env python
# coding:utf-8

""" utils for RaspiCam """

from os.path import exists, isfile
import netifaces
from ConfigParser import Error as ConfigError
from ConfigParser import ConfigParser
from threading import Lock
from raspiserver.logger import APPLOGGER

def get_local_ip():
    """ get local ip address """
    ipaddr = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    return ipaddr

class AppException(Exception):
    """ AppException """
    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

    def __str__(self):
        return repr(self.value)

class Singleton(type):
    """ Singleton """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                    super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class SingletonMixin(object):
    """ Singleton thread safe """
    __singleton_lock = Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        """ get instance """
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance

class VideoCfg(object):
    """ video cfg """
    __metaclass__ = Singleton
    def __init__(self):
        self.width = -1
        self.height = -1
        self.fps = -1
        self.bitrate = -1
        self.brightness = -1

class RecordCfg(object):
    """ record cfg """
    def __init__(self):
        self.base = ''
        self.cycle = None
        self.fsp_limit = -1

class ConfigObject(object):
    """ config object """
    __metaclass__ = Singleton
    def __init__(self):
        # video paramters
        self.video = VideoCfg()
        # record parameters
        self.record = RecordCfg()

class ConfigReader(object):
    """ config file reader """
    def __init__(self, path):
        self.__config = ConfigObject()
        self.__path = path
    def parser(self):
        """ parser func """
        try:
            if exists(self.__path) and isfile(self.__path):
                with open(self.__path) as fhandler:
                    try:
                        config_parser = ConfigParser()
                        config_parser.readfp(fhandler)
                        if config_parser.has_option('video', 'width'):
                            self.__config.video.width = \
                                    config_parser.getint('video', 'width')
                        if config_parser.has_option('video', 'height'):
                            self.__config.video.height = \
                                    config_parser.getint('video', 'height')
                        if config_parser.has_option('video', 'fps'):
                            self.__config.video.fps = \
                                    config_parser.getint('video', 'fps')
                        if config_parser.has_option('video', 'bitrate'):
                            self.__config.video.bitrate = \
                                    config_parser.getint('video', 'bitrate')
                        if config_parser.has_option('video', 'brightness'):
                            self.__config.video.brightness = \
                                    config_parser.getint('video', 'brightness')
                        if config_parser.has_option('record', 'base'):
                            self.__config.record.base = \
                                    config_parser.get('record', 'base')
                        if config_parser.has_option('record', 'cycle'):
                            self.__config.record.cycle = \
                                    config_parser.getboolean('record', 'cycle')
                        if config_parser.has_option('record', 'limit'):
                            self.__config.record.fsp_limit = \
                                    config_parser.getint('record', 'limit')
                    except (AppException, ConfigError) as ex:
                        APPLOGGER.error(ex)
            else:
                raise AppException('config file error')
        except OSError as ex:
            APPLOGGER.error(ex)
        return self.__config

    @property
    def config(self):
        """ config object """
        return self.__config
    def __get_path(self):
        """ get path """
        return self.__path
    def __set_path(self, value):
        """ set path """
        self.__path = value
    path = property(__get_path, __set_path)

def __test():
    """ test function """
    APPLOGGER.debug(get_local_ip())
    try:
        raise AppException('test exp')
    except AppException as ex:
        APPLOGGER.debug(ex)
    config = './config/raspicam.cfg'
    parser = ConfigReader(config)
    parser.parser()
    APPLOGGER.debug(parser.config.video.width)
    APPLOGGER.debug(parser.config.video.height)
    APPLOGGER.debug(parser.config.video.fps)
    APPLOGGER.debug(parser.config.video.bitrate)
    APPLOGGER.debug(parser.config.video.brightness)
    APPLOGGER.debug(parser.config.record.base)
    APPLOGGER.debug(parser.config.record.cycle)
    APPLOGGER.debug(parser.config.record.fsp_limit)

if __name__ == '__main__':
    __test()
