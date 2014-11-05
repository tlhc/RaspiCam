#ifndef TCPREQUEST_H
#define TCPREQUEST_H

#include <QObject>
#include <QTcpSocket>

class TcpRequest: public QObject
{
    Q_OBJECT
public:
    explicit TcpRequest(QObject *parent = 0);
    bool connect(QString host, qint16 port);
private:
    QTcpSocket *_socket;
};

#endif // TCPREQUEST_H
