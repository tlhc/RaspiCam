#ifndef NETSCANER_H
#define NETSCANER_H

#include <QObject>
#include "tcprequest.h"

class NetScaner : public QObject
{
    Q_OBJECT
public:
    explicit NetScaner(QObject *parent = 0);

signals:

public slots:

};

#endif // NETSCANER_H
