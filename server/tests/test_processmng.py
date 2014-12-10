#!/usr/bin/env python
# coding:utf-8
# author TL

""" process manager test """

from unittest import TestCase, main
from raspiserver.processmng import VideoProcessMng
from raspiserver.utils import ConfigReader
from time import sleep

class ProcessMngTest(TestCase):
    """ test process manager """
    def setUp(self):
        """ setup """
        config_parser = ConfigReader('/home/pi/server/config/raspicam.cfg')
        cfg = config_parser.parser()
        self.procssmng = VideoProcessMng(cfg.video)
    def tearDown(self):
        """ tear down """
        pass
    def test_process_start_stop(self):
        """ start process test """
        self.procssmng.getlock()
        try:
            self.procssmng.start()
            sleep(2)
            self.assertTrue(self.procssmng.isrun(), True)
        finally:
            self.procssmng.releaselock()

        self.procssmng.getlock()
        try:
            self.procssmng.stop()
            sleep(2)
        finally:
            self.procssmng.releaselock()

if __name__ == '__main__':
    main()
