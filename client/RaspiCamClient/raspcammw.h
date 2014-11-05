#ifndef RASPCAMMW_H
#define RASPCAMMW_H

#include <QMainWindow>

namespace Ui {
class RaspCamMW;
}

class RaspCamMW : public QMainWindow
{
    Q_OBJECT

public:
    explicit RaspCamMW(QWidget *parent = 0);
    ~RaspCamMW();

private:
    Ui::RaspCamMW *ui;
};

#endif // RASPCAMMW_H
