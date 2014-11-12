#RaspiCam

RaspiCam can be used to capture(server) and play(client) video

![screen:](https://raw.githubusercontent.com/tlhc/RaspiCam/master/client/pics/demo_client.png)

Hardware:

 - RaspiberryPi B+
 - [RPi-Camera-F](http://www.waveshare.net/shop/RPi-Camera-F.htm)
    
Software:

 - Server(written in python, runs on raspbian)
 - Client(written in c++(Qt), runs on ubuntu)

###!!still under development...

###Server:

 - (Capture video use raspivid and Streaming video use vlc)
 - support start, stop video streaming control
 - support remote change video streaming parameters(brightness, fps, bitrate, video width, video height...)
 - support auto discovery
    
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

    - put ctlserver.py in your Rpi then
    - python ctlserver.py

    Client:

    - open with Qt then compile and run


