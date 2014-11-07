#include <QDebug>
#include "tcprequest.h"

TcpRequest::TcpRequest(QObject *parent) :
    QObject(parent) {
    _socket = new QTcpSocket(this);
    connect(_socket, SIGNAL(connected()), this, SLOT(connected()));
    connect(_socket, SIGNAL(disconnected()), this, SLOT(disconnected()));
    connect(_socket, SIGNAL(readyRead()), this, SLOT(readall()));
}

TcpRequest::~TcpRequest() {
    if(_socket != NULL) {
        delete _socket;
        _socket = NULL;
    }
}

bool TcpRequest::connectHost(QHostAddress host, qint16 port, int timeout) {
    QPair <QHostAddress, int> localintf;
    localintf.first = QHostAddress("127.0.0.0");
    localintf.second = 8;
    if(host.isNull() || host.isInSubnet(localintf)) {
        return false;
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

void TcpRequest::close() {
    /*emit disconnected signal*/
    _socket->disconnectFromHost();
}


void TcpRequest::connected() {
    qDebug() << "connected";
}

void TcpRequest::disconnected() {
    _socket->deleteLater();
    qDebug() << "disconnected";
}

void TcpRequest::readall() {
    if(_socket->isReadable()) {
        emit sigmsg(_socket->readAll());
    }
}
