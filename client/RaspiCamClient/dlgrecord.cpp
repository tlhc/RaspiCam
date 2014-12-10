#include "dlgrecord.h"
#include "ui_dlgrecord.h"
#include <QDebug>
#include <QTableWidgetItem>
#include <QPushButton>

DlgRecord::DlgRecord(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DlgRecord)
{
    ui->setupUi(this);
    _extUISetUp();
    _extDataSetUp();
}

void DlgRecord::setData(QHostAddress saddr, quint16 port) {
    if(_pctlc == NULL) {
        _pctlc = new ControlClient(saddr, port);
        connect(_pctlc, SIGNAL(routeOut(QString)), this, SLOT(records(QString)));
        _vodprefix = "http://" + saddr.toString() + ":" + QString::number(_vodport);
    }
}

DlgRecord::~DlgRecord()
{

    if(_pctlc != NULL) {
        delete _pctlc;
        _pctlc = NULL;
    }
    if(_vview != NULL) {
        if(_vview->isStart()) {
            _vview->stop();
        }
        delete _vview;
    }
    if(_mapper != NULL) {
        delete _mapper;
        _mapper = NULL;
    }
    delete ui;
}

void DlgRecord::on_btn_refresh_clicked() {
    if(_pctlc != NULL) {
        _pctlc->get_records();
    }
}

void DlgRecord::records(QString records) {
    ui->tbl_records->clear();  /*clear item also clear signal mapping*/
    reclist.clear();
    reclist = records.split(',');
    ui->tbl_records->setRowCount(reclist.size());
    ui->tbl_records->setColumnCount(2);
    ui->tbl_records->setColumnWidth(0, ui->tbl_records->width() - 130);
    ui->tbl_records->setColumnWidth(1, 80);
    QString item;
    reclist.sort();
    foreach(item, reclist) {
        QTableWidgetItem *tblitem = new QTableWidgetItem();
        QPushButton *delbtn = new QPushButton("Del");
        tblitem->setText(item);
        tblitem->setTextAlignment(Qt::AlignLeft);
        ui->tbl_records->setItem(reclist.indexOf(item), 0, tblitem);
        ui->tbl_records->setCellWidget(reclist.indexOf(item), 1, delbtn);
        connect(delbtn, SIGNAL(clicked()), _mapper, SLOT(map()));
        _mapper->setMapping(delbtn, reclist.indexOf(item));
        qDebug() << item << reclist.indexOf(item);
    }
    connect(_mapper, SIGNAL(mapped(int)), this, SLOT(delclick(int)));
}

void DlgRecord::_extDataSetUp() {
    _pctlc = NULL;
    _mapper = new QSignalMapper(this);
    _vodport = 9001;    //for vod over http
}

void DlgRecord::_extUISetUp() {
    _vview = new VideoView(ui->videow);
    QSize vsize(ui->videow->size());
    _vview->setSize(vsize);
    ui->tbl_records->setEditTriggers(QAbstractItemView::NoEditTriggers);
    ui->tbl_records->horizontalHeader()->setVisible(false);
}

/*for play*/
void DlgRecord::on_tbl_records_cellDoubleClicked(int row, int column) {
    if(_vview->isStart()) {
        _vview->stop();
    }
    if(!_vodprefix.isEmpty()) {
        QString weburl = _vodprefix + ui->tbl_records->item(row, column)->text().trimmed();
        _vview->setWeburl(weburl);
        _vview->start();
    }

}

void DlgRecord::delclick(int row_id) {
    QString filepath = ui->tbl_records->item(row_id, 0)->text();
    if(_pctlc != NULL) {
        _pctlc->rm_records(filepath);
    }
}
