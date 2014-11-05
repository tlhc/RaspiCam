#ifndef RASPCAMMW_H
#define RASPCAMMW_H

#include <QMainWindow>
#include "videoview.h"
#include "tcprequest.h"

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

private:
    void _extUISetUp();
    void _exDataSetUp();
    VideoView *_vview;
    Ui::RaspCamMW *ui;
    QString _streamurl;

};

#endif // RASPCAMMW_H
