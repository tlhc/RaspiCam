#!/usr/bin/env python
# coding:utf-8
# author TL
""" ctl server for Raspberry Pi vlc stream cam DEMO VERSION! """

import os
import sys
import cgi
import time
import signal
import socket
import threading
import netifaces
import SocketServer
import BaseHTTPServer
import logging
import subprocess



def signal_handler(signals, frame):
    """ handle ctrl -c """
    _, _ = signals, frame
    APPLOGGER.info('server exiting..')
    vvpmng = VideoProcessMng()
    vvpmng.getlock()
    try:
        if vvpmng.isset():
            if vvpmng.isrun():
                os.killpg(vvpmng.currpid(), signal.SIGTERM)
    finally:
        vvpmng.releaselock()

    APPLOGGER.info('shutdown complete')
    sys.exit(0)

def loggerinit():
    """ init logger """
    fstr = '%(asctime)s %(levelname)-8s %(funcName)s %(lineno)s %(message)s'
    fomatter = logging.Formatter(fstr)
    _logger = logging.getLogger('ctl_logger')
    _logger.setLevel(logging.DEBUG)
    shandler = logging.StreamHandler()
    fhandler = logging.FileHandler('/home/pi/ctlserver.log')
    shandler.setFormatter(fomatter)
    fhandler.setFormatter(fomatter)
    _logger.addHandler(shandler)
    _logger.addHandler(fhandler)
    return _logger

APPLOGGER = loggerinit()
APPLOGGER.setLevel('DEBUG')

class AppException(Exception):
    """ AppException """
    def __init__(self, value):
        self.value = value
        Exception.__init__(self)

    def __str__(self):
        return repr(self.value)

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
        cmdstr += '-vvv stream:///dev/stdin --sout' + ' '
        if self.record and self.recordfname is not '':
            cmdstr += "'#duplicate{dst=rtp{sdp=rtsp://:" + \
                      str(self.rtsp_port) + '/}' + \
                      ',dst=standard{access=file,mux=mp4,dst=' + \
                      self.recordfname +'.mp4' + "}}'" + ' :demux=h264'
        else:
            cmdstr += "'#rtp{sdp=rtsp://:"
            cmdstr += str(self.rtsp_port) + "/}' :demux=h264"
        return cmdstr


class Singleton(type):
    """ Singleton """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = \
                    super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class VideoProcessMng(object):
    """ VideoProcessMng ensure one video process in thread """
    __metaclass__ = Singleton
    def __init__(self):
        self.vvprocess = None
        self.__process_lock = threading.Lock()
        self.process_cmd = RaspvidCmd()
    def getlock(self):
        """ get lock """
        self.__process_lock.acquire()
    def releaselock(self):
        """ release lock """
        self.__process_lock.release()
    def setprocess(self, process):
        """ set process """
        self.vvprocess = process
    def isset(self):
        """ is set or not """
        if self.vvprocess is not None:
            return True
        return False
    def isrun(self):
        """ is run or not """
        if self.vvprocess is not None and self.vvprocess.poll() is None:
            return True
        return False
    def currpid(self):
        """ return pid """
        return self.vvprocess.pid
    def start(self):
        """ start video process """
        APPLOGGER.info('subcall in porcess')
        child = None
        child = subprocess.Popen(self.process_cmd.cmd(),
                                 shell=True, preexec_fn=os.setsid)
        if child is not None:
            self.vvprocess = child
            APPLOGGER.info('video process start and set')
    def stop(self):
        """ kill video process """
        if self.isset() and self.isrun():
            os.killpg(self.vvprocess.pid, signal.SIGTERM)
            APPLOGGER.info('send video process stoped signal')


class TcpCtlHandler(SocketServer.BaseRequestHandler):
    """ TCPServer RequestHandler """
    def __init__(self, request, client_address, server):
        self.maxbuf = 2048
        self.vvpmng = VideoProcessMng()
        self.clientcmd_start = 'start'
        self.clientcmd_stop = 'stop'
        SocketServer.BaseRequestHandler.__init__(self, request,
                                                 client_address, server)

    def handle(self):
        APPLOGGER.info('theading number is ' + str(threading.activeCount()))
        data = self.request.recv(self.maxbuf)
        self.__process_req(data)

    def __start_process(self):
        """ start video process """
        self.vvpmng.getlock()
        try:
            self.vvpmng.process_cmd.record = False
            self.vvpmng.process_cmd.recordfname = ''
            if not self.vvpmng.isset():
                self.vvpmng.start()
                self.request.sendall(self.vvpmng.process_cmd.cmd())
                APPLOGGER.info('video server run.')
            else:
                if self.vvpmng.isrun():
                    APPLOGGER.info('already run subprocess: ' +
                                   str(self.vvpmng.currpid()))
                    APPLOGGER.info('video process already run.')
                    self.request.sendall(self.clientcmd_start + '|' + '1')
                    self.request.sendall(self.vvpmng.process_cmd.cmd())
                else:
                    APPLOGGER.info('subprocess not running')
            APPLOGGER.info('activeCount is ' + str(threading.activeCount()))
        finally:
            self.vvpmng.releaselock()

    def __stop_process(self):
        """ __stop_process """
        self.vvpmng.getlock()
        try:
            if not self.vvpmng.isset():
                APPLOGGER.warn('no process to stop')
                self.request.sendall(self.clientcmd_stop + '|' + '0')
                return #just jump to finally
            if self.vvpmng.isrun():
                self.vvpmng.stop()
                APPLOGGER.warn('terminating..')
                self.vvpmng.setprocess(None)
                # fake done
                self.request.sendall(self.clientcmd_stop + '|' + '1')
            else:
                APPLOGGER.info('process is terminate')
                self.vvpmng.setprocess(None)
                self.request.sendall(self.clientcmd_stop + '|' + '0')
        finally:
            self.vvpmng.releaselock()

    def __sysinfo(self):
        """ for get cmd """
        ipaddr, _ = self.server.server_address
        vport = self.vvpmng.process_cmd.rtsp_port
        self.request.sendall(str(ipaddr) + ':' + str(vport))

    def __changevprocss(self, data):
        """ change video process paramters
            change|cmd1=opt, cmd2=opt2, ... """
        data = data.lstrip('change|')
        data = data.split(',')
        APPLOGGER.debug(data)
        paradict = {}
        try:
            paradict = dict([item.split('=') for item in data if item != ''])
            if not paradict:
                raise AppException('paradict dict is empty')
        except AppException as ex:
            APPLOGGER.error(ex)
            return

        if 'brightness' in paradict:
            self.vvpmng.process_cmd.bright = int(paradict['brightness'])
        if 'bitrate' in paradict:
            self.vvpmng.process_cmd.bitrate = int(paradict['bitrate'])
        if 'fps' in paradict:
            self.vvpmng.process_cmd.fps = int(paradict['fps'])
        if 'height' in paradict:
            self.vvpmng.process_cmd.height = int(paradict['height'])
        if 'width' in paradict:
            self.vvpmng.process_cmd.width = int(paradict['width'])

        self.vvpmng.getlock()
        try:
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

    def __record(self):
        recdir = '/home/pi/records'
        currtime = time.gmtime()
        rec_sub_dir_name = ''
        rec_sub_dir_name += str(currtime.tm_year) + '_'
        rec_sub_dir_name += str(currtime.tm_mon) + '_'
        rec_sub_dir_name += str(currtime.tm_mday)
        day_recdir = recdir + '/' + rec_sub_dir_name
        filename = str(currtime.tm_hour) + ':' + \
                   str(currtime.tm_min) + ':' + \
                   str(currtime.tm_sec)
        whole_fname = day_recdir + '/' + filename
        if os.path.exists(day_recdir):
            if os.path.isdir(day_recdir):
                if os.path.exists(whole_fname):
                    os.remove(whole_fname)
            else:
                os.remove(day_recdir)
                os.makedirs(day_recdir)
        else:
            os.makedirs(day_recdir)

        self.vvpmng.getlock()
        self.vvpmng.process_cmd.record = True
        self.vvpmng.process_cmd.recordfname = whole_fname
        APPLOGGER.debug(self.vvpmng.process_cmd.cmd())
        try:
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
            self.request.sendall(self.vvpmng.process_cmd.cmd())
            self.vvpmng.releaselock()


    def __process_req(self, data):
        """ process req """
        data = data.strip(' \n')
        if len(data) <= 0:
            return
        if data.lower() == 'start':
            self.__start_process()
        elif data.lower() == 'stop':
            self.__stop_process()
        elif data.lower() == 'get':
            self.__sysinfo()
        elif data.lower().startswith('change'):
            self.__changevprocss(data)
        elif data.lower() == 'record':
            self.__record()
        else:
            APPLOGGER.info('Cmd not support: ' + data)

class TcpCtlServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """ TCPServer """
    allow_reuse_address = True


def __get_local_ip():
    """ get local ip address """
    ipaddr = netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr']
    return ipaddr

def tcpserve(ipaddr, serve_port):
    """ tcpserve """
    try:
        if ipaddr is '':
            raise AppException('get local ip exp')
        if int(serve_port) <= 0 or int(serve_port) > 65535:
            raise AppException('port num err')
    except AppException as ex:
        APPLOGGER.error(ex)

    host, port = ipaddr, int(serve_port)
    server = None
    try:
        server = TcpCtlServer((host, port), TcpCtlHandler)
    except socket.error as ex:
        APPLOGGER.error(ex)
        sys.exit(1)
    APPLOGGER.info('Server Up IP=%s PORT=%s', ipaddr, serve_port)
    if server:
        server.serve_forever()
    else:
        raise AppException('server start err')


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

class HybirdServer(object):
    """ HybirdServer """
    def __init__(self):
        self.__callbacklistdict = {}
        self.thrlist = []
    def setservices(self, name, callback, params):
        """ set services and params """
        self.__callbacklistdict[name] = [callback, params]
    def __preserve(self):
        """ preserve """
        self.thrlist = []
        for name in self.__callbacklistdict.keys():
            _cbinfo = self.__callbacklistdict[name]
            # quick and dirty
            _tmpthr = threading.Thread(target=_cbinfo[0], args=_cbinfo[1])
            _tmpthr.setDaemon(True)
            _tmpthr.setName(name)
            self.thrlist.append(_tmpthr)
    def serve(self):
        """ serve all """
        self.__preserve()
        for item in self.thrlist:
            item.start()
        # none block join ?
        while 1:
            for item in self.thrlist:
                if item is not None and item.isAlive():
                    item.join(1)

def main():
    """ serve for all """
    hyserve = HybirdServer()
    # you can start tcp server or http server
    try:
        local_ip = __get_local_ip()
        tcpctl_port = 9999
        http_port = 8080
        if local_ip == '':
            raise AppException('local ip is empty')
        hyserve.setservices('httpserver', httpserve,
                            (__get_local_ip(), http_port))
        hyserve.setservices('tcpserver', tcpserve,
                            (__get_local_ip(), tcpctl_port))
        hyserve.serve()
    except AppException as ex:
        APPLOGGER.error(ex)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
