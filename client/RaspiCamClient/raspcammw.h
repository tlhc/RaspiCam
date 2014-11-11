#ifndef RASPCAMMW_H
#define RASPCAMMW_H

#include <QMainWindow>
#include <QTimer>
#include <QTime>
#include <QLineEdit>
#include "videoview.h"
#include "tcprequest.h"
#include "netscaner.h"
#include "controlclient.h"

namespace Ui {
class RaspCamMW;
}

class RaspCamMW : public QMainWindow
{
    Q_OBJECT

public:
    explicit RaspCamMW(QWidget *parent = 0);
    ~RaspCamMW();

private slots:
    void on_btnScan_clicked();
    void on_btnStart_clicked();
    void on_btnStop_clicked();
    void on_btnRecord_clicked();
    void recvmsg(QString msg);
    void recvvcmds(QMap<QString, QString> params);
    void laterstart();
    void drawprocess();

    void on_btn_confirm_clicked();

private:
    void _extUISetUp();
    void _exDataSetUp();
    QString _getlecontant(QLineEdit *clts, QString orgkey);
    QString _collectcmd();
    VideoView *_vview;
    Ui::RaspCamMW *ui;
    QString _streamurl;
    NetScaner *scan;
    ControlClient *ctlc;
    QTimer _processtimer;
    QTime _processtime;
    int _cntdown_msec;
    QMap<QString, QString> orgval;
};

#endif // RASPCAMMW_H
