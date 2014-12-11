#include <QApplication>
#include "raspcammw.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    RaspCamMW w;
    w.show();

    return a.exec();
}
