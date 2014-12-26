#include <QDebug>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include "tcprequest.h"

TcpRequest::TcpRequest(QObject *parent, int keep_alive) :
    QObject(parent) {
    _socket = new QTcpSocket(this);
    connect(_socket, SIGNAL(disconnected()), this, SLOT(disconnected()));
    connect(_socket, SIGNAL(readyRead()), this, SLOT(readall()));
    connect(_socket, SIGNAL(error(QAbstractSocket::SocketError)),
            this, SLOT(error(QAbstractSocket::SocketError)));
    connect(_socket, SIGNAL(readChannelFinished()), this, SLOT(readfinished()));
    if(keep_alive == 0) {
        _iskeep = 0;
    } else if(keep_alive == 1) {
        int maxIdle = 30; /* seconds */
        int enableKeepAlive = 1;
        int fd = _socket->socketDescriptor();
        setsockopt(fd, SOL_SOCKET, SO_KEEPALIVE, &enableKeepAlive, sizeof(enableKeepAlive));
        setsockopt(fd, IPPROTO_TCP, TCP_KEEPIDLE, &maxIdle, sizeof(maxIdle));
        _iskeep = 1;
    }
}

TcpRequest::~TcpRequest() {
    if(_socket != NULL) {
        if(_socket->isOpen()) {
            _socket->close();
        }
        _socket->deleteLater();
    }
}

bool TcpRequest::connectHost(QHostAddress host, qint16 port, int timeout) {
    QPair <QHostAddress, int> localintf;
    localintf.first = QHostAddress("127.0.0.0");
    localintf.second = 8;
    if(host.isNull() || host.isInSubnet(localintf)) {
        return false;
    }
    if(_socket->isOpen()) {
        _socket->abort();
    }
    _socket->connectToHost(host, port);
    return _socket->waitForConnected(timeout);
}

bool TcpRequest::sendData(QByteArray data) {
    if(_socket->isWritable()) {
        if(_socket->write(data, data.length()) == data.length()) {
            return true;
        }
    }
    return false;
}

void TcpRequest::disconnectHost() {
    /*emit disconnected signal auto*/
    _socket->disconnectFromHost();
}

void TcpRequest::reset() {
    if(_socket->isOpen()) {
        _socket->abort();
    }
}

bool TcpRequest::isconnected() {
    if(_socket != NULL) {
        if(_socket->state() == QAbstractSocket::ConnectedState) {
            if(_socket->isOpen() && _socket->isReadable() && _socket->isWritable()) {
                return true;
            }
        }
    }
    return false;
}

bool TcpRequest::isprocessing() {
    if(_socket != NULL) {
        if(_socket->state() == QAbstractSocket::ConnectingState) {
            return true;
        }
    }
    return false;
}

int TcpRequest::status() {
    return _socket->state();
}

void TcpRequest::disconnected() {
    if(_socket != NULL) {
        _socket->abort();
    }
    if(_iskeep == 0) {
        ;
    }
}

void TcpRequest::readall() {
    if(_socket->isReadable()) {
        while(!_socket->atEnd()) {
            _alldata += _socket->read(2048);
        }
    }
}


void TcpRequest::error(QAbstractSocket::SocketError error) {
    if(error == QAbstractSocket::ConnectionRefusedError) {
        _socket->abort();
    }
}

void TcpRequest::readfinished() {
    emit sigmsg(_alldata);
    emit done();
    _alldata.clear();
}
