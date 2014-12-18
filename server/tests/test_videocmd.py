#!/usr/bin/env python
# coding:utf-8
# author TL

""" test for video cmd """

from unittest import TestCase, main
from raspiserver.videocmd import RaspvidCmd
from raspiserver.utils import ConfigReader

class VideoCMDTest(TestCase):
    def setUp(self):
        """ setup """
        config_parser = ConfigReader('/home/pi/server/config/raspicam.cfg')
        cfg = config_parser.parser()
        cmd = RaspvidCmd(cfg.video)
        self.cmd = cmd
    def tearDown(self):
        """ tear down """
        pass
    def test_generate_cmd(self):
        """ test generate cmd """
        cmdstr = ("raspivid -br 50 -w 1280 -h 800 -b 4500000 -fps 30 "
                  "-vf -hf -t 0 -o - | cvlc --sout-rtp-caching=10 "
                  "stream:///dev/stdin "
                  "--sout '#rtp{sdp=rtsp://:9000/}' :demux=h264")
        self.assertEqual(self.cmd.cmd(), cmdstr)
    def test_change_cmd(self):
        """ change cmd """
        self.cmd.bitrate = 10000000
        self.cmd.fps = 40
        self.cmd.width = 400
        self.cmd.height = 900
        self.cmd.bright = 60
        cmdstr = ("raspivid -br 60 -w 400 -h 900 -b 10000000 -fps 40 "
                  "-vf -hf -t 0 -o - | cvlc --sout-rtp-caching=10 "
                  "stream:///dev/stdin "
                  "--sout '#rtp{sdp=rtsp://:9000/}' :demux=h264")
        self.assertEqual(self.cmd.cmd(), cmdstr)
    def test_record_cmd(self):
        """ test record cmd """
        self.cmd.record = True
        self.cmd.recordfname = 'test_record.mp4'
        cmdstr = ("raspivid -br 50 -w 1280 -h 800 -b 4500000 -fps 30 "
                  "-vf -hf -t 0 -o - | cvlc --sout-rtp-caching=10 "
                  "stream:///dev/stdin "
                  "--sout '#duplicate{dst=rtp{sdp=rtsp://:9000/},"
                  "dst=standard{access=file,mux=mp4,"
                  "dst=test_record.mp4.mp4}}' :demux=h264")
        self.assertEqual(self.cmd.cmd(), cmdstr)

if __name__ == '__main__':
    main()
