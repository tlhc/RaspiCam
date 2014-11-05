#include "tcprequest.h"

TcpRequest::TcpRequest(QObject *parent) :
    QObject(parent) {
    _socket = new QTcpSocket(this);
}

bool TcpRequest::connect(QString host, qint16 port) {
    if(host.length() > 0) {
        _socket->connectToHost(host, port);
        return _socket->waitForConnected(1000);
    }
}
