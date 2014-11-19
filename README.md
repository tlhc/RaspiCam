#RaspiCam

RaspiCam can be used to capture(server) and play(client) video

![screen:](https://raw.githubusercontent.com/tlhc/RaspiCam/master/client/pics/demo_client.png)


![screen-web:](https://raw.githubusercontent.com/tlhc/RaspiCam/master/client/pics/web.png)

Hardware:

 - RaspiberryPi B+
 - [RPi-Camera-F](http://www.waveshare.net/shop/RPi-Camera-F.htm)
    
Software:

 - Server(written in python, runs on raspbian)
 - Client(written in c++(Qt), runs on ubuntu)

###!!still under development...

    depends on libvlc: libvlc may support Qt5 as well, but on my ubuntu, many
    software depends on libGuiQt4.so I tend not to remove libGuiQt4 or modify $PATH(may have effect)
    so if you want use Qt5 with libvlc , just do it . ^V^

###Server:

 - (Capture video use raspivid and Streaming video use vlc)
 - support start, stop video streaming control
 - support remote change video streaming parameters(brightness, fps, bitrate, video width, video height...)
 - support auto discovery
 - support web access(control)
    
###Client:

 - (Play video use libvlc based on Qt)
 - support auto discovery Rpi(just push scan button)
 - support start, stop control
 - support remote change Rpi video streaming parameters(brightness, fps, bitrate, video width, video height...)


##Installation

    before use :
    check Server(RaspiberryPi) installed these components:
    python-dev -- sudo apt-get install python-dev
    pyhton-pip -- sudo apt-get install python-pip
    vlc        -- sudo apt-get install vlc
    netifaces  -- sudo pip install netifaces

    *may be has other packeges or components not mentioned above you may install 
    by yourself.*

##Useage:

    Server:

    - put server dir in your Rpi(one folder) then
    - cd server
    - python ctlserver.py

    Client:

    - open with Qt then compile and run
    - (or) 

        ```bash
          - cd RaspiCamClient
          - qmake
          - make
        ```



    sorry for my poor english
