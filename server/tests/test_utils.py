#!/usr/bin/env python
# coding:utf-8
# author TL

""" utils test """
from unittest import TestCase, main
from raspiserver.utils import ConfigReader, get_local_ip

class UtilsTest(TestCase):
    """ test utils function """
    def test_get_local_ip(self):
        """ test get_local_ip """
        self.assertEqual('192.168.1.108', get_local_ip())
    def test_config_reader(self):
        """ test get config """
        config = './config/raspicam.cfg'
        parser = ConfigReader(config)
        cfg = parser.parser()

        self.assertEqual(cfg.comm_port.tcp_port, 9999)
        self.assertEqual(cfg.comm_port.http_port, 8080)
        self.assertEqual(cfg.comm_port.vod_port, 9001)

        self.assertEqual(cfg.video.width, 1280)
        self.assertEqual(cfg.video.height, 800)
        self.assertEqual(cfg.video.bitrate, 4500000)
        self.assertEqual(cfg.video.brightness, 50)
        self.assertEqual(cfg.video.fps, 30)
        self.assertEqual(cfg.video.rtsp_port, 9000)

        self.assertEqual(cfg.record.base, "'/home/pi/records'")
        self.assertEqual(cfg.record.cycle, True)
        self.assertEqual(cfg.record.fsp_limit, 3700)

if __name__ == '__main__':
    main()

