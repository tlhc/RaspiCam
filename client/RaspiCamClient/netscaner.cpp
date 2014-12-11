#include <QNetworkAddressEntry>
#include <QNetworkInterface>
#include <QHostAddress>
#include <QStringList>
#include <QTimer>
#include <QEventLoop>
#include <QDebug>
#include "netscaner.h"

ScanWorker::ScanWorker(QString intfname, QHostAddress iprange, QHostAddress netmask) :
    _intfname(intfname),
    _iprange(iprange),
    _netmask(netmask)
{

}

void ScanWorker::process() {

    quint32 netaddr = _iprange.toIPv4Address() & _netmask.toIPv4Address();
    quint32 wildmask = ~_netmask.toIPv4Address();
    for(quint32 address = netaddr + 1; address < netaddr + wildmask; address++) {
        TcpRequest _request;
        if(_request.connectHost(QHostAddress(address), 9999, 10)) {
            /*_request is async so we may not sendData here
             * thread may exit before the request return
            */
            emit getone(QHostAddress(address).toString());
        }
        _request.disconnectHost();
    }
    emit finished();
}

NetScaner::NetScaner(QObject *parent) : QObject(parent)
{
    QList<QNetworkInterface> _intflist;
    _intflist = QNetworkInterface::allInterfaces();
    //construct worker list
    QList<QNetworkInterface>::iterator iter = _intflist.begin();
    int avflag = QNetworkInterface::IsUp | QNetworkInterface::IsRunning |
                 QNetworkInterface::CanBroadcast | QNetworkInterface::CanMulticast;
    for(; iter != _intflist.end(); iter++) {
        if((*iter).flags() != avflag) {
            continue;
        }
        QList<QNetworkAddressEntry> tmp = (*iter).addressEntries();
        QNetworkAddressEntry entry;
        foreach (entry, tmp) {
            if(entry.ip().protocol() == QAbstractSocket::IPv4Protocol) {
                qDebug() << (*iter).name() << entry.ip() << entry.netmask();
                _workerlist.append(new ScanWorker((*iter).name(), entry.ip(), entry.netmask()));
            }
        }
    }
    for(int i = 0; i < _workerlist.size(); i++) {
        _thrlist.append(new QThread(this));
    }
    for(int i = 0; i < _workerlist.size(); i++) {
        _workerlist.at(i)->moveToThread(_thrlist.at(i));
        connect(_workerlist.at(i), SIGNAL(error(QString)), this, SLOT(error(QString)));
        connect(_workerlist.at(i), SIGNAL(getone(QString)), this, SLOT(getone(QString)));
        connect(_thrlist.at(i), SIGNAL(started()), _workerlist.at(i), SLOT(process()));
        connect(_workerlist.at(i), SIGNAL(finished()), _thrlist.at(i), SLOT(quit()));
    }
}

NetScaner::~NetScaner()
{
    /*TODO .. CHECK*/
    qDeleteAll(_workerlist.begin(), _workerlist.end());
    _workerlist.clear();

    qDeleteAll(_thrlist.begin(), _thrlist.end());
    _thrlist.clear();
}

void NetScaner::start() {
    for(int i = 0; i < _workerlist.size(); i++) {
        if(!_thrlist.at(i)->isRunning()) {
            _thrlist.at(i)->start();
        }
    }
}

QString NetScaner::ret() const {
    return _ret;
}

void NetScaner::error(QString err) {
    qDebug() << Q_FUNC_INFO << err;
}

void NetScaner::getone(QString one) {
    QEventLoop loop;
    TcpRequest vreq;
    connect(&vreq, SIGNAL(done()), &loop, SLOT(quit()));
    if(vreq.connectHost(QHostAddress(one), 9999, 100)) {
        connect(&vreq, SIGNAL(sigmsg(QString)), this, SLOT(verityslot(QString)));
        vreq.sendData("get");
    }
    /*when send get command then loop start*/
    loop.exec();
}

void NetScaner::verityslot(QString msg) {
    if(_verifymsg(msg)) {
        emit routeOut(msg);
    }
}

bool NetScaner::_verifymsg(QString msg) {
    if(msg.isEmpty()) {
        return false;
    }
    QStringList splist = msg.split(":");
    if(splist.length() == 2) {
        QHostAddress _host;
        bool ok = false;
        int _port = splist.at(1).toInt(&ok);
        if(_host.setAddress(splist.at(0)) && ok && (_port > 0 && _port < 65535)) {
            return true;
        }
    }
    return false;
}
