#ifndef CONTROLCLIENT_H
#define CONTROLCLIENT_H

#include <QObject>
#include <QHostAddress>
#include <QMap>
#include "tcprequest.h"

class ControlClient : public QObject
{
    Q_OBJECT
public:
    explicit ControlClient(QHostAddress server, qint16 port, QObject *parent = 0);
    ~ControlClient();
    void start();
    void stop();
    void change(QString params);
signals:
    void routeOut(QMap<QString, QString>);
public slots:
    void servermsg(QString msg);
private:
    QMap<QString, QString> _parsecmd(QString cmdstr);
    QString _parsepara(QString para);
    QHostAddress _serveraddr;
    qint16 _port;
    TcpRequest *_request;
    QString _raspcmd_prefix;
};

#endif // CONTROLCLIENT_H
