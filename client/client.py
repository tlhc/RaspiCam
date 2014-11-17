#!/usr/bin/env python
# coding:utf-8

""" test cmd program for client """
import socket
import sys



def main():
    """ client test """
    host, port = "192.168.1.105", 9999
    data = " ".join(sys.argv[1:])
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        sock.sendall(data + "\n")
        received = sock.recv(2048)
    finally:
        sock.close()
    print "Sent:     {}".format(data)
    print "Received: {}".format(received)

if __name__ == '__main__':
    main()
