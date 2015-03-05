#ifndef VIDEOVIEW_H
#define VIDEOVIEW_H

#include <QWidget>
#include <vlc/vlc.h>

class VideoView : public QWidget
{
    Q_OBJECT
public:
    explicit VideoView(QWidget *parent = 0);
    ~VideoView();
    void start();
    void stop();
    void snapshot(const QString &name);

    void startRecording(const QString& filePath);
    void stopRecording();
    bool isRecording() const { return _recording; }
    bool isStart() const {return _start; }

    QSize videoSize() const;
    void setSize(const QSize &size);
    QSize sizeHint() const;
    QString weburl() const;
    void setWeburl(const QString &weburl);
    int getvideolen();
    void setposition(float pos);
    float getposition() const;
    libvlc_state_t getvideostat() ;

private:
    void closeEvent(QCloseEvent* event);

private:
    libvlc_instance_t* _vlcInstance;
    libvlc_media_player_t* _vlcMediaPlayer;
    bool _recording;
    bool _start;
    QString _recordingFilePath;
    QString _weburl;
};

#endif // VIDEOVIEW_H
