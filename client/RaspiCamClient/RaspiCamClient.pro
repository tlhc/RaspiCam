#-------------------------------------------------
#
# Project created by QtCreator 2014-11-05T15:32:53
#
#-------------------------------------------------

QT       += core gui network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = RaspiCamClient
TEMPLATE = app


SOURCES += main.cpp\
        raspcammw.cpp \
    videoview.cpp \
    tcprequest.cpp \
    netscaner.cpp

HEADERS  += raspcammw.h \
    videoview.h \
    tcprequest.h \
    netscaner.h

FORMS    += raspcammw.ui


unix:LIBS += -lvlc
