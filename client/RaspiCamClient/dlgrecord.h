#ifndef DLGRECORD_H
#define DLGRECORD_H

#include <QDialog>
#include <QStringList>
#include <QSignalMapper>
#include <QTimer>
#include "videoview.h"
#include "controlclient.h"

namespace Ui {
class DlgRecord;
}

class DlgRecord : public QDialog
{
    Q_OBJECT

public:
    explicit DlgRecord(QWidget *parent = 0);
    void setData(QHostAddress saddr, quint16 port, quint16 vodport);
    ~DlgRecord();

private slots:
    void on_btn_refresh_clicked();
    void records(QString records);
    void on_tbl_records_cellDoubleClicked(int row, int column);
    void delclick(int row_id);
    void setplaypos();

private:
    Ui::DlgRecord *ui;
    ControlClient *_pctlc;
    void _extDataSetUp();
    void _extUISetUp();
    QStringList reclist;
    VideoView *_vview;
    QSignalMapper *_mapper;
    quint16 _vodport;
    QString _vodprefix;
    QTimer *_processtimer;
    static bool _fLess(QString file1, QString file2);
};

#endif // DLGRECORD_H
