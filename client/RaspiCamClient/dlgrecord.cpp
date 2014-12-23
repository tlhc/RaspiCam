#include <QTableWidgetItem>
#include <QPushButton>
#include <QDateTime>
#include <QDebug>
#include "dlgrecord.h"
#include "ui_dlgrecord.h"


DlgRecord::DlgRecord(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::DlgRecord)
{
    ui->setupUi(this);
    _extUISetUp();
    _extDataSetUp();
}

void DlgRecord::setData(QHostAddress saddr, quint16 port, quint16 vodport) {
    if(_pctlc == NULL) {
        if(vodport == 0) {
            _vodport = 9001;    //default port
        } else {
            _vodport = vodport;
        }
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
    if(_processtimer->isActive()) {
        _processtimer->stop();
    }
    delete _processtimer;
    delete ui;
}

void DlgRecord::on_btn_refresh_clicked() {
    if(_pctlc != NULL) {
        _pctlc->get_records();
    }
}

void DlgRecord::records(QString records) {
    QStringList cmdlist = records.split("|");

    if(!(cmdlist.length() == 2 &&
       QString::compare(cmdlist[0], "records", Qt::CaseInsensitive) == 0)) {
        return;
    }
    records.clear();
    records = cmdlist[1];
    //qDebug() << records;
    ui->tbl_records->clear();  /*clear item also clear signal mapping*/
    reclist.clear();
    reclist = records.split(',');
    ui->tbl_records->setRowCount(reclist.size());
    ui->tbl_records->setColumnCount(2);
    ui->tbl_records->setColumnWidth(0, ui->tbl_records->width() - 130);
    ui->tbl_records->setColumnWidth(1, 80);
    QString item;
    qSort(reclist.begin(), reclist.end(), DlgRecord::_fLess);
    //reclist.sort();
    foreach(item, reclist) {
        QTableWidgetItem *tblitem = new QTableWidgetItem();
        QPushButton *delbtn = new QPushButton("Del");
        tblitem->setText(item);
        tblitem->setTextAlignment(Qt::AlignLeft);
        ui->tbl_records->setItem(reclist.indexOf(item), 0, tblitem);
        ui->tbl_records->setCellWidget(reclist.indexOf(item), 1, delbtn);
        connect(delbtn, SIGNAL(clicked()), _mapper, SLOT(map()));
        _mapper->setMapping(delbtn, reclist.indexOf(item));
        //qDebug() << item << reclist.indexOf(item);
    }
    connect(_mapper, SIGNAL(mapped(int)), this, SLOT(delclick(int)));
}

void DlgRecord::_extDataSetUp() {
    _pctlc = NULL;
    _mapper = new QSignalMapper(this);
    _vodport = 0;      //for vod over http
    _processtimer = new QTimer(this);
    _processtimer->setInterval(500);
    connect(_processtimer, SIGNAL(timeout()), this, SLOT(setplaypos()));
}

void DlgRecord::_extUISetUp() {
    _vview = new VideoView(ui->videow);
    QSize vsize(ui->videow->size());
    _vview->setSize(vsize);
    ui->tbl_records->setEditTriggers(QAbstractItemView::NoEditTriggers);
    ui->tbl_records->horizontalHeader()->setVisible(false);
    ui->btn_acc_reject->button(QDialogButtonBox::Cancel)->hide();
}

bool DlgRecord::_fLess(QString file1, QString file2) {
    file1 = file1.remove(".mp4");
    file2 = file2.remove(".mp4");
    QDateTime weight1, weight2;
    QStringList ymdlist1 = file1.split("/").filter("_");
    QStringList ymdlist2 = file2.split("/").filter("_");
    QStringList hmslist1 = file1.split("/").filter(":");
    QStringList hmslist2 = file2.split("/").filter(":");
    if(ymdlist1.length() == 1 && ymdlist2.length() == 1 &&
            hmslist1.length() == 1 && hmslist2.length() == 1) {
        QStringList rymd1 = ymdlist1[0].split("_");
        QStringList rymd2 = ymdlist2[0].split("_");
        QStringList rhms1 = hmslist1[0].split(":");
        QStringList rhms2 = hmslist2[0].split(":");
        if(rymd1.length() == 3 && rymd2.length() == 3
                && rhms1.length() == 3 && rhms2.length() == 3) {
            weight1.setDate(QDate(rymd1[0].toInt(), rymd1[1].toInt(), rymd1[2].toInt()));
            weight1.setTime(QTime(rhms1[0].toInt(), rhms1[1].toInt(), rhms1[2].toInt()));
            weight2.setDate(QDate(rymd2[0].toInt(), rymd2[1].toInt(), rymd2[2].toInt()));
            weight2.setTime(QTime(rhms2[0].toInt(), rhms2[1].toInt(), rhms2[2].toInt()));

            if (weight1 <= weight2) {
                return true;
            }
        }
    }
    return false;
}


/*for play*/
void DlgRecord::on_tbl_records_cellDoubleClicked(int row, int column) {
    if(_vview->isStart()) {
        _vview->stop();
    }
    if(_processtimer->isActive()) {
        _processtimer->stop();
    }
    if(!_vodprefix.isEmpty()) {
        QString weburl = _vodprefix + ui->tbl_records->item(row, column)->text().trimmed();
        _vview->setWeburl(weburl);
        _vview->start();
    }
    QTimer::singleShot(500, _processtimer, SLOT(start())); /*need time to get video length*/
}

void DlgRecord::delclick(int row_id) {
    QString filepath = ui->tbl_records->item(row_id, 0)->text();
    if(_pctlc != NULL) {
        _pctlc->rm_records(filepath);
    }
}

void DlgRecord::setplaypos() {
    int len = _vview->getvideolen();
    ui->video_silder->setMinimum(0);
    ui->video_silder->setMaximum(len);
    float currpos = 0.0;
    currpos = _vview->getposition();
    ui->video_silder->setSliderPosition(currpos * len);
    libvlc_state_t status = _vview->getvideostat();
    if(status == libvlc_Ended || status == libvlc_Stopped || status == libvlc_Error) {
        _processtimer->stop();
        _vview->stop();
        ui->video_silder->setSliderPosition(0);
    }
}
