#!/usr/bin/env python
# coding:utf-8
# author TL

""" video cmd generator """

from raspiserver.logger import APPLOGGER

class RaspvidCmd(object):
    """ opt the cmd str """
    def __init__(self, cfg):
        self.fps = cfg.fps if cfg.fps != -1 else 30
        # 0 - 100
        self.bright = cfg.brightness if cfg.brightness != -1 else 50
        # 4.5MBit/s
        self.bitrate = cfg.bitrate if cfg.bitrate != -1 else 4500000
        self.rtsp_port = cfg.rtsp_port if cfg.rtsp_port != 0 else 9000
        self.width = cfg.width if cfg.width != -1 else 1280
        self.height = cfg.height if cfg.height != -1 else 720
        self.stime = 0         # forever
        self.record = False
        self.recordfname = ''

    def cmd(self):
        """ return cmd str """
        raspvidbase = 'raspivid'
        vlcbase = 'cvlc'
        cmdstr = ''
        cmdstr += raspvidbase + ' '
        cmdstr += '-br ' + str(self.bright) + ' '
        cmdstr += '-w ' + str(self.width) + ' '
        cmdstr += '-h ' + str(self.height) + ' '
        cmdstr += '-b '  + str(self.bitrate) + ' '
        cmdstr += '-fps ' + str(self.fps) + ' '
        cmdstr += '-vf -hf' + ' '
        cmdstr += '-t ' + str(self.stime) + ' '
        cmdstr += '-o -' + ' '

        cmdstr += '|' + ' '
        cmdstr += vlcbase + ' ' + '--sout-rtp-caching=10' + ' '
        cmdstr += 'stream:///dev/stdin --sout' + ' '
        if self.record and self.recordfname is not '':
            cmdstr += "'#duplicate{dst=rtp{sdp=rtsp://:" + \
                      str(self.rtsp_port) + '/}' + \
                      ',dst=standard{access=file,mux=mp4,dst=' + \
                      self.recordfname +'.mp4' + "}}'" + ' :demux=h264'
        else:
            cmdstr += "'#rtp{sdp=rtsp://:"
            cmdstr += str(self.rtsp_port) + "/}' :demux=h264"
        return cmdstr

def __test():
    """ test function """
    from raspiserver.utils import ConfigReader
    cfg_parser = ConfigReader('./config/raspicam.cfg')
    cfg = cfg_parser.parser()
    videocmd = RaspvidCmd(cfg.video)
    APPLOGGER.debug(videocmd.cmd())

if __name__ == '__main__':
    __test()

