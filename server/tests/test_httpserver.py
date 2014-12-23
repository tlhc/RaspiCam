#!/usr/bin/env python
# coding:utf-8
# author TL

""" HttpServerTest """

from unittest import TestCase, main
from raspiserver.utils import ConfigReader
from raspiserver.recordmng import RecordMng
from raspiserver.utils import get_local_ip
from raspiserver.processmng import VideoProcessMng
from raspiserver.httpserver import httpserve
from time import sleep
import threading
import requests

class HttpServerTest(TestCase):
    """ HttpServerTest """
    IsSetup = False
    def setUp(self):
        self.test_url = 'http://' + get_local_ip() + ':8080'
        if not self.IsSetup:
            self.setup_class()
            self.testthr = None
            self.__class__.IsSetup = True
    def setup_class(self):
        """ real setup """
        TestCase.setUp(self)
        config_parser = ConfigReader('/home/pi/server/config/raspicam.cfg')
        cfg = config_parser.parser()
        # test in local(Rpi)
        recmng = RecordMng(cfg.record)
        vvpmng = VideoProcessMng(cfg.video)
        self.testthr = threading.Thread(target=httpserve, \
                                        args=(cfg, recmng, vvpmng))
        self.testthr.setDaemon(True)
        self.testthr.start()

    def tearDown(self):
        pass

    def test_get(self):
        """ get test status_code """
        resp = requests.request('GET', self.test_url)
        self.assertEqual(200, resp.status_code)
    def test_post_start(self):
        """ test start command """
        resp = requests.post(self.test_url + '/start')
        self.assertEqual(resp.status_code, 200)
        config_parser = ConfigReader('/home/pi/server/config/raspicam.cfg')
        cfg = config_parser.parser()
        vvpmng = VideoProcessMng(cfg.video)
        self.assertEqual(resp.text, vvpmng.process_cmd.cmd())
        sleep(5)
    def test_post_stop(self):
        """ test stop command """
        resp = requests.post(self.test_url + '/stop')
        self.assertEqual(resp.status_code, 200)
    def test_post_change(self):
        """ test post change command """
        params = {'para_fps' : '30',
                  'para_bright' : '50',
                  'para_bitrate' : '5000000',
                  'para_width' : '1204',
                  'para_height': '768'}
        resp = requests.post(self.test_url + '/change', data=params)
        self.assertEqual(resp.status_code, 200)
        sleep(5)
        resp = requests.post(self.test_url + '/stop')
        self.assertEqual(resp.status_code, 200)
    def test_post_record(self):
        """ test record command """
        resp = requests.post(self.test_url + '/record')
        self.assertEqual(resp.status_code, 200)
        sleep(5)
        resp = requests.post(self.test_url + '/stop')
        self.assertEqual(resp.status_code, 200)

if __name__ == '__main__':
    main()
