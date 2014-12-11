#ifndef TCPREQUEST_H
#define TCPREQUEST_H

#include <QObject>
#include <QTcpSocket>
#include <QHostAddress>

class TcpRequest: public QObject
{
    Q_OBJECT
public:
    explicit TcpRequest(QObject *parent = 0, int keep_alive = 0);
    ~TcpRequest();
    bool connectHost(QHostAddress host, qint16 port, int timeout);
    bool sendData(QByteArray data);
    void disconnectHost();
    void reset();
    bool isconnected();
    bool isprocessing();
    int status();
private:
    QTcpSocket *_socket;
    int _iskeep;
signals:
    void sigmsg(QString msg);
    void done();
public slots:
    void disconnected();
    void readall();
    void error(QAbstractSocket::SocketError error);
};

#endif // TCPREQUEST_H
