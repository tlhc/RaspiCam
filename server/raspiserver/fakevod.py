#!/usr/bin/env python
# coding:utf-8

""" vod server base vlc vod over http feature
    JUST FOR TCP Server USE"""

import BaseHTTPServer
from os.path import isfile, exists
from socket import error as sockerror
from raspiserver.utils import AppException
from SocketServer import ThreadingMixIn
from raspiserver.logger import APPLOGGER


class VodServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """ vod server over http """
    def __init__(self, server_address, RequestHandler):
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandler)


class VodReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
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
                fhandler = open(self.path)
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(fhandler.read())
                fhandler.close()
            return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)


def vodserve(ipaddr, serve_port):
    """ vod serve """
    try:
        if ipaddr is '':
            raise AppException('get local ip exp')
        if int(serve_port) <= 0 or int(serve_port) > 65535:
            raise AppException('port num err')
    except AppException as ex:
        APPLOGGER.error(ex)
    APPLOGGER.info('Server Up IP=%s PORT=%s', ipaddr, serve_port)
    server = None
    try:
        server = VodServer((ipaddr, serve_port), VodReqHandler)
    except sockerror as ex:
        APPLOGGER.error(ex)
        exit(1)
    if server:
        server.serve_forever()
    else:
        APPLOGGER.error('vod server start error')

def __run():
    """ test run """
    from raspiserver.utils import get_local_ip
    server, port = get_local_ip(), 9001
    vodserve(server, port)

if __name__ == '__main__':
    __run()


