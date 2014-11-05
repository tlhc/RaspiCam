#include "raspcammw.h"
#include "ui_raspcammw.h"

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
}

void RaspCamMW::on_btnScan_clicked() {

}

void RaspCamMW::on_btnStart_clicked() {
    if(!_vview->isStart()) {
        _vview->start();
    }
}

void RaspCamMW::on_btnStop_clicked() {
    if(_vview->isStart()) {
        _vview->stop();
    }
}


void RaspCamMW::on_btnRecord_clicked()
{

}
