#include "raspcammw.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    RaspCamMW w;
    w.show();

    return a.exec();
}
