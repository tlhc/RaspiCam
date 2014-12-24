#!/usr/bin/env python
# coding:utf-8
# author TL

""" logger """

import logging
import logging.handlers

def loggerinit():
    """ init logger """
    fstr = '%(asctime)s %(levelname)-8s %(funcName)s %(lineno)s %(message)s'
    log_fname = '/tmp/ctlserver.log'
    fomatter = logging.Formatter(fstr)
    _logger = logging.getLogger('ctl_logger')
    _logger.setLevel(logging.DEBUG)
    shandler = logging.StreamHandler()
    fhandler = logging.handlers.RotatingFileHandler(log_fname,
                                                    maxBytes=1024 * 1024,
                                                    backupCount=5)
    shandler.setFormatter(fomatter)
    fhandler.setFormatter(fomatter)
    _logger.addHandler(shandler)
    _logger.addHandler(fhandler)
    return _logger

APPLOGGER = loggerinit()
APPLOGGER.setLevel('DEBUG')
