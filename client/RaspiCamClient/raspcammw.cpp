#include <QDir>
#include "tcprequest.h"
#include "ui_raspcammw.h"
#include "raspcammw.h"
#include "dlgrecord.h"



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
    if(_vview != NULL) {
        if(_vview->isStart()) {
            _vview->stop();
        }
        delete _vview;
    }
    if(ctlc != NULL) {
        delete ctlc;
    }
    if(scan != NULL) {
        delete scan;
    }
    delete ui;
}

void RaspCamMW::_extUISetUp() {
    _vview = new VideoView(ui->videow);
    QSize vsize(ui->videow->size());
    _vview->setSize(vsize);
    ui->btnRecord->setEnabled(false);
    ui->btnStart->setEnabled(false);
    ui->btnStop->setEnabled(false);
    ui->btn_confirm->setEnabled(false);
    ui->le_bright->setEnabled(false);
    ui->le_BitRate->setEnabled(false);
    ui->le_fps->setEnabled(false);
    ui->le_height->setEnabled(false);
    ui->le_width->setEnabled(false);
    ui->btn_remoteRcd->setEnabled(false);
    ui->btn_getrecord->setEnabled(false);
    ui->btnSnap->setEnabled(false);
}

void RaspCamMW::_exDataSetUp() {
    _streamurl = "";
    ctlc = NULL;
    scan = new NetScaner();
    connect(scan, SIGNAL(routeOut(QString)), this, SLOT(recvmsg(QString)));
    _processtimer.setInterval(1000);
    connect(&_processtimer, SIGNAL(timeout()), this, SLOT(drawprocess()));
    _cntdown_msec = 5000;
    _ctlport = 9999;
    _vodport = 0;
}

QString RaspCamMW::_getlecontant(QLineEdit *clts, QString orgkey) {
    if(clts == NULL) {
        return "";
    }
    bool ok = false;
    int val = clts->text().toInt(&ok);
    if(!ok) {
        if(orgval.contains(orgkey)) {
            val = orgval[orgkey].toInt(); //here should be success
        } else {
            val = 0;
        }
    }
    return QString::number(val);
}


QString RaspCamMW::_collectcmd() {
    QString _base = "brightness=";
    _base += _getlecontant(ui->le_bright, "brightness");
    _base += ",";

    _base += "bitrate=";
    _base += _getlecontant(ui->le_BitRate, "bitrate");
    _base += ",";

    _base += "width=";
    _base += _getlecontant(ui->le_width, "width");
    _base += ",";

    _base += "height=";
    _base += _getlecontant(ui->le_height, "height");
    _base += ",";


    _base += "fps=";
    _base += _getlecontant(ui->le_fps, "fps");
    _base += ",";
    return _base;
}

void RaspCamMW::on_btnScan_clicked() {
    scan->start();
}

void RaspCamMW::on_btnStart_clicked() {
    if(!_vview->isStart()) {
        if(ctlc != NULL) {
            ctlc->start();
            _vview->setWeburl(_streamurl);
            _processtimer.start();
            _processtime.restart();
            QTimer::singleShot(_cntdown_msec, this, SLOT(laterstart()));
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
    if(!_vview->isStart()) {
        return;
    }
    if(!_vview->isRecording()) {
        _vview->startRecording("./recordfile.mp4");
        ui->btnRecord->setText("Stop Record");
    } else {
        _vview->stopRecording();
        ui->btnRecord->setText("Record");
    }
}


void RaspCamMW::recvmsg(QString msg) {
    _streamurl.clear();
    _streamurl = "rtsp://";
    _streamurl = _streamurl + msg + "/";
    ui->lbl_address->setText("address: " + _streamurl);
    ui->btnRecord->setEnabled(true);
    ui->btnStart->setEnabled(true);
    ui->btnStop->setEnabled(true);
    ui->btn_remoteRcd->setEnabled(true);

    ui->btn_confirm->setEnabled(true);
    ui->le_bright->setEnabled(true);
    ui->le_BitRate->setEnabled(true);
    ui->le_fps->setEnabled(true);
    ui->le_height->setEnabled(true);
    ui->le_width->setEnabled(true);
    ui->btn_getrecord->setEnabled(true);
    ui->btnSnap->setEnabled(true);


    //verify in netscaner so no need to verify here
    QStringList _tmplist = msg.split(":");
    _saddr = QHostAddress(_tmplist.at(0));
    if(!_saddr.isNull()) {
        if (ctlc != NULL) {
            delete ctlc;
            ctlc = NULL;
        }
        ctlc = new ControlClient(_saddr, 9999); //ctl port
        connect(ctlc, SIGNAL(routeOut(QMap<QString,QString>)),
                this, SLOT(recvvcmds(QMap<QString,QString>)));
        connect(ctlc, SIGNAL(routeOut(QString)),
                this, SLOT(recvcmdstr(QString)));
        if(ctlc != NULL) {
            ctlc->get_vodport();
            ctlc->get_currparams();
        }
    }

}

void RaspCamMW::recvvcmds(QMap<QString, QString> params) {
    if(params.size() > 0) {

        orgval = params;
        if(params.contains("width")) {
            ui->le_width->setText(params["width"]);
        }
        if(params.contains("height")) {
            ui->le_height->setText(params["height"]);
        }
        if(params.contains("bitrate")) {
            ui->le_BitRate->setText(params["bitrate"]);
        }
        if(params.contains("brightness")) {
            ui->le_bright->setText(params["brightness"]);
        }
        if(params.contains("fps")) {
            ui->le_fps->setText(params["fps"]);
        }
    }
}

void RaspCamMW::recvcmdstr(QString cmd) {
    QStringList cmdlist = cmd.split("|");
    if(cmdlist.length() != 2) {
        return;
    }
    if(QString::compare(cmdlist[0], "vodport", Qt::CaseInsensitive) == 0) {
        _vodport = cmdlist[1].toInt();
        disconnect(ctlc, SIGNAL(routeOut(QString)),
                   this, SLOT(recvcmdstr(QString)));
    }
}

void RaspCamMW::laterstart() {

    if(_vview != NULL) {
        if(!_vview->isStart()) {
            _vview->start();
        }
    }
}

void RaspCamMW::drawprocess() {
    if(_processtime.elapsed() < _cntdown_msec) {
        QString full;
        int getbit = _processtime.elapsed() / 1000;
        for(int i = 0; i < _cntdown_msec / 1000; i++) {
            if(i <= getbit) {
                full.push_back("*");
            } else {
                full.push_back("-");
            }
        }
        ui->lblprocess->setText(full);
    } else {
        ui->lblprocess->setText("");
        _processtimer.stop();
    }
}


void RaspCamMW::on_btn_confirm_clicked() {
    if(ctlc != NULL) {
        ctlc->change(_collectcmd());
    }
    if(_vview->isStart()) {
        _vview->stop();
    }
    _vview->setWeburl(_streamurl);
    _processtimer.start();
    _processtime.restart();
    QTimer::singleShot(_cntdown_msec, this, SLOT(laterstart()));
}


void RaspCamMW::on_btn_remoteRcd_clicked() {
    if(_vview->isStart()) {
        _vview->stop();
    }
    if(ctlc != NULL) {
        ctlc->record();
        _vview->setWeburl(_streamurl);
        _processtimer.start();
        _processtime.restart();
        QTimer::singleShot(_cntdown_msec, this, SLOT(laterstart()));
    }
}

void RaspCamMW::on_btn_getrecord_clicked() {
    DlgRecord *dlg = new DlgRecord(this);
    if (!_saddr.isNull()) {
        dlg->setData(_saddr, _ctlport, _vodport);
        dlg->exec();
    }
    delete dlg;
}

void RaspCamMW::on_btnSnap_clicked() {
    if(_vview->isStart()) {
        if(!QDir::current().entryList(QDir::Dirs).contains("snapshots")) {
            QDir current = QDir::current();
            if(!current.mkdir(QDir::currentPath() + QString("/snapshots"))) {
                return;
            }
        }
        QString sname = "./snapshots/snapshot_";
        sname.append(QDateTime::currentDateTime().toString("yyyy_MM_dd-hh:mm:ss"));
        sname.append(".png");    //default to png
        _vview->snapshot(sname);
    }
}
