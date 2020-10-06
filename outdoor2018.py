__author__ = "Akshay Unnikrishnan"
__copyright__ = "Copyright 2007, The Leak detector  Project"
__credits__ = ["Rob Knight", "Peter Maxwell", "Gavin Huttley",
                    "Matthew Wakefield"]
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Akshay Unnikrishnan"
__email__ = "akshay.u2909@gmail.com"
__status__ = "Prototype"


#
# THIS IS THE OUTDOOR MODULE CODE WHICH COMPARES THE IMAGES OF THE WATERMETER DIAL
# WITH LAST 5 IMAGES AND BASED ON THE DIFF VALUE MAKES A DECISION IF WATER IS FLOWING 
# OR NOT. IF THE WATER FLOW DETECTED IT PUBLISHES A ON MESSAGE IN THE MQTT CHANNEL CALLED WATER_USAGE
#


import os
import time
import cv2
import numpy as np 
from collections import deque
import random
import paho.mqtt.client as mqtt
from picamera import PiCamera
from diffimg import diff

MQTT_SERVER = "piINDOOR"
MQTT_CHANNEL = "WATER_USAGE"
MQTT_PORT = 1883

camera = PiCamera()

def on_publish(client,userdata,result): #create function for callback
    #print("data published \n")
    pass
client = mqtt.Client("SENSOR")  
client.on_publish = on_publish 
client.connect(MQTT_SERVER, MQTT_PORT)  



def isImageSame(image1, image2):
    if not image1 or not image2:
        print("One of the image is empty. So returning True")
        return True

    diffVal = diff(image1, image2)	
    print("Difference between " + image1 + " and " + image2 + " is : " + str(diffVal))
    if diffVal < 0.01 :
        return True
    else:
        return False


# Step 1
# Initialize an infinite loop for taking picture and comparing them to previous images
# in timeline to detect leak

#Initialize Leak Detected flag to false
leakDetected = False

#print("Leak Usage state is " +  str(leakDetected))

imageList = []

MAX_IMAGES = 5

index = 0
leakCounter = 0
noleakCounter = 0

queue = deque(["", "", "", "", ""])


while True:
#   print("Leak Usage state is " +  str(leakDetected))

#   Step 2
#   Take a pictures in random intervals of 1-5 so that the dial is 
    time.sleep(random.randint(5,10))

    index += 1


    currImage = "Image" + str(index) + ".jpg"

    #camera.start_preview()
    #print("Taking Picture " + currImage)
    camera.capture(currImage)
    #camera.stop_preview()

    isSame = True
    for image in queue:
        if not isImageSame(currImage, image):
            isSame = False
            break

    if isSame :  
        print("No Water usage detected")
        client.publish(MQTT_CHANNEL,"off") 
    else :
        print("Most certainly water is flowing")
        client.publish(MQTT_CHANNEL,"on") 

#   Now add the image to the queue
    queue.append(currImage)
    tempImage = queue.popleft()    
    #print(queue)
    #print("Delete image file " + tempImage)
    if tempImage:
        os.remove(tempImage)
