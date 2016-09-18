import pygame.camera as cam
import pygame.image as im
from time import sleep
import os
from os import path
from serial import Serial
import uuid

################
# prep section #
################

dirname = "neural_photos"

if(not path.isdir(dirname)):
    os.mkdir(dirname)
os.chdir(dirname)

minpulse = 55
maxpulse = 240

#######################
# Arduino Serial bind #
#######################

devserial = "/dev/ttyUSB0"
ardserial = Serial(devserial, 9600) # default arduino clock?

####################
# Cam init section #
####################
cam.init()
mycam = cam.Camera("/dev/video0",(1280,720))
mycam.start()
image = None
pulse = 80.0
try:
    while 1:
        if mycam.query_image():
            image = mycam.get_image()
            try:
                pulseraw = float(ardserial.readline())-15
                pulse = pulseraw if minpulse <= pulseraw <= maxpulse and abs(pulse-pulseraw)<20 else pulse
            except:
                pass
            im.save(image, "{}_{}.jpg".format(pulse, uuid.uuid4().hex))
            print("created img!", image, pulse, pulseraw)
            sleep(5)
        else:
            sleep(0.01)
except KeyboardInterrupt:
    mycam.stop()
    ardserial.close()

