#ifndef CONTROLCLIENT_H
#define CONTROLCLIENT_H

#include <QObject>
#include "tcprequest.h"
#include <QHostAddress>

class ControlClient : public QObject
{
    Q_OBJECT
public:
    explicit ControlClient(QHostAddress server, qint16 port, QObject *parent = 0);
    void start();
    void stop();
signals:

public slots:
    void servermsg(QString msg);
private:
    QHostAddress _serveraddr;
    qint16 _port;
    TcpRequest* _request;

};

#endif // CONTROLCLIENT_H
