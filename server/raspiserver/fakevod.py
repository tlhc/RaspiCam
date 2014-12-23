#!/usr/bin/env python
# coding:utf-8
# author TL

""" vod server base vlc vod over http feature
    JUST FOR TCP Server use"""

import sys
import BaseHTTPServer
from os.path import isfile, exists
from socket import error as sockerror
from raspiserver.utils import AppException
from SocketServer import ThreadingMixIn
from raspiserver.logger import APPLOGGER

VOD_FILE = ''

def getvodfile():
    """ get the in use video file name """
    return VOD_FILE

def _setvodfile(filename):
    """ set vod file in use """
    global VOD_FILE
    VOD_FILE = filename

class VODServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """ vod server over http """
    def __init__(self, server_address, RequestHandler):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandler)

class VODReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ vod request handler """
    def __init__(self, request, client_address, server):
        self.server = server
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request,
                                                       client_address, server)
    def do_GET(self):
        """ handle video request """
        APPLOGGER.info(self.path)
        if not exists(self.path) or not isfile(self.path) \
                or not self.path.endswith('mp4'):
            self.send_error(404, 'File Not Found: %s' % self.path)
            return
        try:
            sendreply = False
            if self.path.endswith('.mp4'):
                mimetype = 'video/mp4'
                sendreply = True

            if sendreply == True:
                # Open the static file requested and send it
                _setvodfile(self.path)
                fhandler = open(self.path)
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(fhandler.read())
                fhandler.close()
            return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
        finally:
            _setvodfile('')


def vodserve(cfg):
    """ vod serve """
    ipaddr = cfg.comm_port.address
    serve_port = cfg.comm_port.vod_port
    try:
        if ipaddr is '':
            raise AppException('get local ip exp')
        if int(serve_port) <= 0 or int(serve_port) > 65535:
            raise AppException('port num err')
    except AppException as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    APPLOGGER.info('Server Up IP=%s PORT=%s', ipaddr, serve_port)
    server = None
    try:
        server = VODServer((ipaddr, serve_port), VODReqHandler)
    except sockerror as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    if server:
        server.serve_forever()
    else:
        APPLOGGER.error('vod server start error')

def __run():
    """ test run """
    from raspiserver.utils import ConfigReader
    config_path = './config/raspicam.cfg'
    cfg_parser = ConfigReader(config_path)
    cfg = cfg_parser.parser()
    vodserve(cfg)

if __name__ == '__main__':
    __run()


