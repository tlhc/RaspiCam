#!/usr/bin/env python
# coding:utf-8

""" logger """

import logging

def loggerinit():
    """ init logger """
    fstr = '%(asctime)s %(levelname)-8s %(funcName)s %(lineno)s %(message)s'
    fomatter = logging.Formatter(fstr)
    _logger = logging.getLogger('ctl_logger')
    _logger.setLevel(logging.DEBUG)
    shandler = logging.StreamHandler()
    fhandler = logging.FileHandler('/home/pi/ctlserver.log')
    shandler.setFormatter(fomatter)
    fhandler.setFormatter(fomatter)
    _logger.addHandler(shandler)
    _logger.addHandler(fhandler)
    return _logger

APPLOGGER = loggerinit()
APPLOGGER.setLevel('DEBUG')
