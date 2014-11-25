#!/usr/bin/env python
# coding:utf-8

""" video cmd generator """

from logger import APPLOGGER

class RaspvidCmd(object):
    """ opt the cmd str """
    def __init__(self):
        self.fps = 30
        self.bright = 50       # 0 - 100
        self.bitrate = 4500000 # 4.5MBit/s
        self.rtsp_port = 9000
        self.width = 1280
        self.height = 720
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
        cmdstr += vlcbase + ' '
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

if __name__ == '__main__':
    VIDEOCMD = RaspvidCmd()
    APPLOGGER.debug(VIDEOCMD.cmd())

