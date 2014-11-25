#!/usr/bin/env python
# coding:utf-8

""" utils for RaspiCam """

import netifaces
from logger import APPLOGGER

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

if __name__ == '__main__':
    APPLOGGER.debug(get_local_ip())
    try:
        raise AppException('test exp')
    except AppException as ex:
        APPLOGGER.debug(ex)

