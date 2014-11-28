#!/usr/bin/env python
# coding:utf-8

""" TcpServerTest"""

from unittest import TestCase, main
from raspiserver.utils import ConfigReader
from raspiserver.recordmng import RecordMng
from raspiserver.utils import get_local_ip
from raspiserver.processmng import VideoProcessMng
from raspiserver.tcpserver import tcpserve
from time import sleep
import threading
import socket

class TCPServerTest(TestCase):
    """ TCPServerTest """
    IsSetup = False
    def setUp(self):
        self.test_ipaddr = get_local_ip()
        self.test_server_port = 9999
        if not self.IsSetup:
            self.setup_class()
            self.testthr = None
            self.__class__.IsSetup = True
    def setup_class(self):
        """ real setup """
        TestCase.setUp(self)
        config_parser = ConfigReader('/home/pi/server/config/raspicam.cfg')
        cfg = config_parser.parser()
        server, port = get_local_ip(), 9999
        recmng = RecordMng(cfg.record)
        vvpmng = VideoProcessMng(cfg.video)
        self.testthr = threading.Thread(target=tcpserve, \
                args=(server, port, cfg, recmng, vvpmng))
        self.testthr.setDaemon(True)
        self.testthr.start()

    def tearDown(self):
        pass

    def __sendmsg(self, msg):
        """ send msg """
        con_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        readmsg = ''
        try:
            con_sock.connect((self.test_ipaddr, self.test_server_port))
            con_sock.sendall(msg + '\n')
            readmsg = con_sock.recv(2048)
        finally:
            con_sock.close()
        return readmsg

    @classmethod
    def __get_process_cmd(cls):
        """ get process_cmd """
        config_parser = ConfigReader('/home/pi/server/config/raspicam.cfg')
        cfg = config_parser.parser()
        vvpmng = VideoProcessMng(cfg.video)
        return vvpmng.process_cmd.cmd()
    def test_get(self):
        """ get command test """
        recvmsg = self.__sendmsg('get')
        self.assertEqual(recvmsg, self.test_ipaddr + ':' \
                + str(9000))    # 9000 is rtsp port

    def test_tcp_start(self):
        """ test start command """
        recvmsg = self.__sendmsg('start')
        process_cmd = self.__get_process_cmd()
        # self.assertEqual(recvmsg, process_cmd)
        sleep(5)
    def test_tcp_stop(self):
        """ test tcp stop command """
        recvmsg = self.__sendmsg('stop')
        # self.assertEqual(recvmsg, 'stop|1')
    def test_tcp_change(self):
        """ test tcp change command """
        cmd_str = ('fps=30,brightness=50,bitrate=4500000,'
                   'width=768,height=1280')
        cmd_str = 'change|' + cmd_str
        print cmd_str
        recvmsg = self.__sendmsg(cmd_str)
        process_cmd = self.__get_process_cmd()
        # self.assertEqual(recvmsg, process_cmd)
        sleep(5)
        recvmsg = self.__sendmsg('stop')
        # self.assertEqual(recvmsg, 'stop|1')
    def test_tcp_record(self):
        """ test record command """
        recvmsg = self.__sendmsg('record')
        process_cmd = self.__get_process_cmd()
        # self.assertEqual(recvmsg, process_cmd)
        sleep(5)
        recvmsg = self.__sendmsg('stop')
        # self.assertEqual(recvmsg, 'stop|1')

if __name__ == '__main__':
    main()
