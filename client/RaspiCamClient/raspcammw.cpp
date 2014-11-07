#include <QTimer>
#include "raspcammw.h"
#include "ui_raspcammw.h"
#include "tcprequest.h"


RaspCamMW::RaspCamMW(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::RaspCamMW)
{
    ui->setupUi(this);
    _exDataSetUp();
    _extUISetUp();
}

RaspCamMW::~RaspCamMW()
{
    delete ui;
}

void RaspCamMW::_extUISetUp() {
    _vview = new VideoView(ui->videow);
    QSize vsize(ui->videow->size());
    _vview->setSize(vsize);
    ui->btnRecord->setEnabled(false);
    ui->btnStart->setEnabled(false);
    ui->btnStop->setEnabled(false);
}

void RaspCamMW::_exDataSetUp() {
    _streamurl = "";
    scan = new NetScaner();
    connect(scan, SIGNAL(routeOut(QString)), this, SLOT(recvmsg(QString)));
    ctlc = NULL;
}

void RaspCamMW::on_btnScan_clicked() {
    scan->start();

}

void RaspCamMW::on_btnStart_clicked() {
    if(!_vview->isStart()) {
        if(ctlc != NULL) {
            ctlc->start();
            _vview->setWeburl(_streamurl);
            _vview->start();
        }

    }
}

void RaspCamMW::on_btnStop_clicked() {
    if(_vview->isStart()) {
        if(ctlc != NULL) {
            ctlc->stop();
        }
        _vview->stop();
    }
}


void RaspCamMW::on_btnRecord_clicked() {

}


void RaspCamMW::recvmsg(QString msg) {
    _streamurl.clear();
    _streamurl = "rtsp://";
    _streamurl = _streamurl + msg + "/";
    ui->lbl_address->setText("address: " + _streamurl);
    ui->btnRecord->setEnabled(true);
    ui->btnStart->setEnabled(true);
    ui->btnStop->setEnabled(true);

    //verify in netscaner so no need to verify here
    QStringList _tmplist = msg.split(":");
    QHostAddress address(_tmplist.at(0));
    ctlc = new ControlClient(address, 9999); //ctl port
}
