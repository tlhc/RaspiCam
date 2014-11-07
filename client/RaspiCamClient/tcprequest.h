#ifndef TCPREQUEST_H
#define TCPREQUEST_H

#include <QObject>
#include <QTcpSocket>
#include <QHostAddress>

class TcpRequest: public QObject
{
    Q_OBJECT
public:
    explicit TcpRequest(QObject *parent = 0);
    ~TcpRequest();
    bool connectHost(QHostAddress host, qint16 port, int timeout);
    bool sendData(QByteArray data);
    void close();
private:
    QTcpSocket *_socket;
signals:
    void sigmsg(QString msg);
public slots:
    void connected();
    void disconnected();
    void readall();
};

#endif // TCPREQUEST_H
