#!/usr/bin/env python
# coding:utf-8
# author TL

""" record mng test """

from unittest import TestCase, main
from raspiserver.recordmng import RecordMng
from raspiserver.utils import ConfigReader

class RecordMngTest(TestCase):
    """ record manager test """
    def setUp(self):
        cfg_parser = ConfigReader('./config/raspicam.cfg')
        cfg = cfg_parser.parser()
        self.recordmng = RecordMng(cfg.record)
    def tearDown(self):
        pass
    def test_record_start(self):
        """ record start test """
        pass

if __name__ == '__main__':
    main()

