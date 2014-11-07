#ifndef NETSCANER_H
#define NETSCANER_H

#include <QObject>
#include <QThread>
#include <QList>
#include <QMap>
#include <QString>
#include <QNetworkInterface>
#include "tcprequest.h"


class ScanWorker : public QObject {
    Q_OBJECT
public:
    ScanWorker(QString intfname, QHostAddress iprange, QHostAddress netmask);
public slots:
    void process();
signals:
    void finished();
    void error(QString err);
    void getone(QString one);
private:
    QString _intfname;
    QHostAddress _iprange;
    QHostAddress _netmask;
};

class NetScaner : public QObject
{
    Q_OBJECT
public:
    explicit NetScaner(QObject *parent = 0);
    ~NetScaner();
    void start();
    QString ret() const;

signals:
    void routeOut(QString);
public slots:
    void error(QString err);
    void getone(QString one);
    void verityslot(QString msg);
private:
    bool _verifymsg(QString msg);
private:
    QList<QThread *> _thrlist;
    QList<ScanWorker *> _workerlist;
    QString _ret;
    QString _iprange;
    QString _netmask;
};

#endif // NETSCANER_H
