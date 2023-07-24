import serial
import time
from random import randint

startMarker = '<'
endMarker = '>'
dataStarted = False
dataBuf = ""
messageComplete = False
prev_send = time.time()

def setupSerial(baudRate, serialPortName):
    
    global  serialPort
    
    serialPort = serial.Serial(port= serialPortName, baudrate = baudRate, timeout=0, rtscts=True)

    print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))

    waitForArduino()


def sendToArduino(stringToSend):
    
        # this adds the start- and end-markers before sending
    global startMarker, endMarker, serialPort
    
    stringWithMarkers = (startMarker)
    stringWithMarkers += stringToSend
    stringWithMarkers += (endMarker)

    serialPort.write(stringWithMarkers.encode('utf-8')) # encode needed for Python3



def recvLikeArduino():

    global startMarker, endMarker, serialPort, dataStarted, dataBuf, messageComplete

    if serialPort.inWaiting() > 0 and messageComplete == False:
        x = serialPort.read().decode("utf-8") # decode needed for Python3
        
        if dataStarted == True:
            if x != endMarker:
                dataBuf = dataBuf + x
            else:
                dataStarted = False
                messageComplete = True
        elif x == startMarker:
            dataBuf = ''
            dataStarted = True
    
    if (messageComplete == True):
        messageComplete = False
        return dataBuf
    else:
        return "XXX" 


def waitForArduino():

    # wait until the Arduino sends 'Arduino is ready' - allows time for Arduino reset
    # it also ensures that any bytes left over from a previous message are discarded
    
    print("Waiting for Arduino to reset")
     
    msg = ""
    while msg.find("READY") == -1:
        msg = recvLikeArduino()
        if not (msg == 'XXX'): 
            print(msg)


def send_pos(position):
    # global prev_send
    # if time.time() - prev_send > 0.25:
    cmd_text = f"{position} 0"
    sendToArduino(cmd_text)
    print(f"sent {cmd_text} to arudino!")
        # prev_send = time.time()


if __name__ == "__main__":
    setupSerial(115200, "/dev/ttyACM0")
    # count = 0
    # prevTime = time.time()
    while True:
        # arduinoReply = recvLikeArduino()
        # if not (arduinoReply == 'XXX'):
        #     print ("Time %s  Reply %s" %(time.time(), arduinoReply))
            
        # if time.time() - prevTime > 0.25:
        #     sendToArduino("this is a test " + str(count))
        #     prevTime = time.time()
        #     count += 1
        # for i in range(10):
        delay = 0.5
        # print(f"new position in {(delay - (time.time() - prev_send)) * 100}...")
        if time.time() - prev_send > delay:
            p = randint(200,400)
            send_pos(p)
            print(f"{19*(p-200)/200}cm")
            prev_send = time.time()
