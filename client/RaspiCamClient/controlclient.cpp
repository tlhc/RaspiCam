#include "controlclient.h"


ControlClient::ControlClient(QHostAddress server, qint16 port, QObject *parent) :
    QObject(parent),
    _serveraddr(server),
    _port(port)
{
    _request = new TcpRequest(this);
    connect(_request, SIGNAL(sigmsg(QString)), this, SLOT(servermsg(QString)));
}

void ControlClient::start() {
    if(_request->connectHost(_serveraddr, _port, 100)) {
        _request->sendData("start");
    }
}

void ControlClient::stop() {
    if(_request->connectHost(_serveraddr, _port, 100)) {
        _request->sendData("stop");
    }
}

void ControlClient::servermsg(QString msg) {
    qDebug() << msg;
}
