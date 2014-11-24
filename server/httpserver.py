#!/usr/bin/env python
# coding:utf-8

""" http server """
import os
import sys
import cgi
import socket
import threading
import SocketServer
import BaseHTTPServer
from logger import APPLOGGER
from utils import get_local_ip
from utils import AppException
from processmng import VideoProcessMng


class HttpCtlHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ HttpHandler for GET and POST """
    def __init__(self, request, client_address, server):
        self.vvpmng = VideoProcessMng()
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request,
                                                       client_address, server)
    def __sendmsg(self, code, msg):
        """ send msg to client """
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(msg)
    def do_GET(self):
        """ GET """
        if self.path == '/':
            self.path = '/index.html'
        try:
            # Check the file extension required and
            # set the right mime type
            sendreply = False
            if self.path.endswith('.html'):
                mimetype = 'text/html'
                sendreply = True
            if self.path.endswith('.jpg'):
                mimetype = 'image/jpg'
                sendreply = True
            if self.path.endswith('.gif'):
                mimetype = 'image/gif'
                sendreply = True
            if self.path.endswith('.js'):
                mimetype = 'application/javascript'
                sendreply = True
            if self.path.endswith('.css'):
                mimetype = 'text/css'
                sendreply = True

            if sendreply == True:
                # Open the static file requested and send it
                fhandler = open(os.curdir + os.sep + self.path)
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(fhandler.read())
                fhandler.close()
            return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def __start_process(self):
        """ start the video process """
        self.vvpmng.getlock()
        self.vvpmng.process_cmd.record = False
        self.vvpmng.process_cmd.recordfname = ''
        try:
            if not self.vvpmng.isset():
                self.vvpmng.start()
                self.__sendmsg(200, self.vvpmng.process_cmd.cmd())
                APPLOGGER.info('video server run.')
            else:
                if self.vvpmng.isrun():
                    APPLOGGER.info('already run subprocess: ' +
                                   str(self.vvpmng.currpid()))
                    APPLOGGER.info('video process already run.')
                    self.__sendmsg(200, 'already run')
                else:
                    APPLOGGER.info('subprocess not running')
            APPLOGGER.info('activeCount is ' + str(threading.activeCount()))
        finally:
            self.vvpmng.releaselock()

    def __stop_process(self):
        """ stop the video process """
        self.vvpmng.getlock()
        try:
            if not self.vvpmng.isset():
                APPLOGGER.warn('no process to stop')
                self.__sendmsg(200, 'no process to stop')
                return # jump to finally
            if self.vvpmng.isrun():
                self.vvpmng.stop()
                APPLOGGER.warn('terminating..')
                self.vvpmng.setprocess(None)
                self.__sendmsg(200, 'terminating..')
            else:
                APPLOGGER.info('process is terminate')
                self.vvpmng.setprocess(None)
                self.__sendmsg(200, 'process is terminated')
        finally:
            self.vvpmng.releaselock()

    def __changevprocss(self, form):
        """ change video process params """
        self.vvpmng.getlock()
        try:
            def getvalue(src):
                """ set value """
                retval = -1
                try:
                    retval = int(src)
                except ValueError as ex:
                    APPLOGGER.warn(ex)
                return retval
            def setpara(key, form, dst):
                """ set params """
                if key in form.keys():
                    tmpval = -1
                    tmpval = getvalue(form[key].value)
                    if tmpval != -1:
                        dst = tmpval
                return dst

            self.vvpmng.process_cmd.bright = \
                    setpara('para_bright', form, self.vvpmng.process_cmd.bright)
            self.vvpmng.process_cmd.fps = \
                    setpara('para_fps', form, self.vvpmng.process_cmd.fps)
            self.vvpmng.process_cmd.bitrate = \
                    setpara('para_bitrate', form, \
                    self.vvpmng.process_cmd.bitrate)
            self.vvpmng.process_cmd.width = \
                    setpara('para_width', form, self.vvpmng.process_cmd.width)
            self.vvpmng.process_cmd.height = \
                    setpara('para_height', form, self.vvpmng.process_cmd.height)

            APPLOGGER.debug(self.vvpmng.process_cmd.cmd())
            self.__sendmsg(200, self.vvpmng.process_cmd.cmd())

            if not self.vvpmng.isset():
                self.vvpmng.start()
                return
            if self.vvpmng.isrun():
                self.vvpmng.stop()
                self.vvpmng.setprocess(None)
                self.vvpmng.start()
            else:
                self.vvpmng.start()
        finally:
            self.vvpmng.releaselock()

    def do_POST(self):
        """ POST """
        APPLOGGER.debug(self.path)
        _environ = {'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': self.headers['Content-Type'],}
        form = cgi.FieldStorage(fp=self.rfile,
                                headers=self.headers,
                                environ=_environ)
        if self.path == '/start':
            self.__start_process()
            return
        elif self.path == '/stop':
            self.__stop_process()
            return
        elif self.path == '/change':
            self.__changevprocss(form)
            return
        else:
            APPLOGGER.debug(str(form))
            self.send_response(503)
            self.end_headers()
            return


class HttpCtlServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """ ThreadedHTTPServer """
    allow_reuse_address = True


def httpserve(ipaddr, serve_port):
    """ httpserve """
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
        server = HttpCtlServer((ipaddr, serve_port), HttpCtlHandler)
    except socket.error as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    if server:
        server.serve_forever()
    else:
        APPLOGGER.error('http server start error')


if __name__ == '__main__':
    SERVER, PORT = get_local_ip(), 8080
    httpserve(SERVER, PORT)
