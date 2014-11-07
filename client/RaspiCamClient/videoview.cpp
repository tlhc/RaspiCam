#include "videoview.h"

static const char* vlcArguments[] = {
    "--intf=dummy",
    "--ignore-config",
    "--no-media-library",
    "--no-one-instance",
    "--no-osd",
    "--no-snapshot-preview",
    "--no-stats",
    "--no-audio",
    "--no-video-title-show",
    "-vvv"
};

VideoView::VideoView(QWidget *parent) :
    QWidget(parent),
    _vlcInstance(libvlc_new(sizeof(vlcArguments) / sizeof(vlcArguments[0]), vlcArguments)),
    _vlcMediaPlayer(0),
    _recording(false),
    _start(false) {

    setAutoFillBackground(true);
    QPalette palette = this->palette();
    palette.setColor(QPalette::Window, Qt::black);
    setPalette(palette);
}

VideoView::~VideoView() {
    libvlc_release(_vlcInstance);
}

void VideoView::start() {
    Q_ASSERT(!_vlcMediaPlayer);

    if(_weburl.length() <= 0 || !_weburl.startsWith("rtsp://")) {
        return;
    }
    libvlc_media_t* vlcMedia = libvlc_media_new_location(_vlcInstance, _weburl.toStdString().c_str());
    if (_recording) {
        Q_ASSERT(!_recordingFilePath.isEmpty());

        // FIXME: Some of these parameters could be configurable.
        const char* recordingOptionPattern =
                "sout=#duplicate{"
                    "dst=display,"
                    "dst='transcode{vcodec=theo,vb=1800,acodec=vorb,ab=128}:standard{access=file,dst=%1}'"
                "}";

        QString recordingOption = QString(recordingOptionPattern).arg(_recordingFilePath);
        libvlc_media_add_option(vlcMedia, recordingOption.toUtf8().constData());
        libvlc_media_add_option(vlcMedia, "v4l2-caching=100");
    }

    _vlcMediaPlayer = libvlc_media_player_new_from_media(vlcMedia);
    libvlc_media_release(vlcMedia);

#if defined(Q_OS_LINUX)
    libvlc_media_player_set_xwindow(_vlcMediaPlayer, winId());
#elif defined(Q_OS_MAC)
    libvlc_media_player_set_nsobject(m_vlcMediaPlayer, winId());
#elif defined(Q_OS_WIN)
    libvlc_media_player_set_hwnd(m_vlcMediaPlayer, (void *)this->winId());
#else
//#error "unsupported platform"
#endif

    libvlc_media_player_play(_vlcMediaPlayer);
    _start = true;
}

void VideoView::stop() {
    Q_ASSERT(_vlcMediaPlayer);

    libvlc_media_player_stop(_vlcMediaPlayer);
    libvlc_media_player_release(_vlcMediaPlayer);
    _vlcMediaPlayer = 0;
    _start = false;
}

void VideoView::takeSnapshot(const QString &filePath) {
    Q_ASSERT(_vlcMediaPlayer);

    libvlc_video_take_snapshot(_vlcMediaPlayer, 0, filePath.toUtf8().constData(), 0, 0);
}

void VideoView::startRecording(const QString &filePath) {
    Q_ASSERT(_vlcMediaPlayer);
    Q_ASSERT(!_recording);

    _recording = true;
    _recordingFilePath = filePath;
    stop();
    start();
}

void VideoView::stopRecording() {
    Q_ASSERT(_vlcMediaPlayer);
    Q_ASSERT(_recording);

    _recording = false;
    _recordingFilePath.clear();
    stop();
    start();
}

void VideoView::setSize(const QSize &size) {
    if(size.isValid()) {
        this->setMinimumSize(size.width(), size.height());
        this->setMaximumSize(size.width(), size.height());
    }
    return;
}

QSize VideoView::sizeHint() const {
    return QSize(400, 300);
}

void VideoView::closeEvent(QCloseEvent *event) {
    stop();
    QWidget::closeEvent(event);
}

QString VideoView::weburl() const {
    return _weburl;
}

void VideoView::setWeburl(const QString &weburl) {
    _weburl = weburl;
}