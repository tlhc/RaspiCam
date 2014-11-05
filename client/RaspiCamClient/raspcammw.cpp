#include "raspcammw.h"
#include "ui_raspcammw.h"

RaspCamMW::RaspCamMW(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::RaspCamMW)
{
    ui->setupUi(this);
}

RaspCamMW::~RaspCamMW()
{
    delete ui;
}
