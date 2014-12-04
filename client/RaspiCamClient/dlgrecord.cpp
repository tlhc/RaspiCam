#include "dlgrecord.h"
#include "ui_dlgrecord.h"
#include <QDebug>
#include <QTableWidgetItem>

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
    delete ui;
}

void DlgRecord::on_btn_refresh_clicked() {
    if(_pctlc != NULL) {
        _pctlc->get_records();
    }
}

void DlgRecord::records(QString records) {
    ui->tbl_records->clear();
    reclist.clear();
    reclist = records.split(',');
    ui->tbl_records->setRowCount(reclist.size());
    ui->tbl_records->setColumnCount(1);
    ui->tbl_records->setColumnWidth(0, ui->tbl_records->width() - 20);
    QString item;
    foreach(item, reclist) {
        QTableWidgetItem *tblitem = new QTableWidgetItem();
        tblitem->setText(item);
        tblitem->setTextAlignment(Qt::AlignLeft);
        ui->tbl_records->setItem(reclist.indexOf(item), 0, tblitem);
        qDebug() << item << reclist.indexOf(item);
    }
}

void DlgRecord::_extDataSetUp() {
    _pctlc = NULL;
}

void DlgRecord::_extUISetUp() {
    _vview = new VideoView(ui->videow);
    QSize vsize(ui->videow->size());
    _vview->setSize(vsize);
    ui->tbl_records->setEditTriggers(QAbstractItemView::NoEditTriggers);
    ui->tbl_records->horizontalHeader()->setVisible(false);
}


void DlgRecord::on_tbl_records_cellDoubleClicked(int row, int column) {
    qDebug() << ui->tbl_records->item(row, column)->text();
}
