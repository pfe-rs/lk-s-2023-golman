import serial
import time

startMarker = '<'
endMarker = '>'

dataStarted = False
dataBuf = ""
messageComplete = False


def setupSerial(baudRate, serialPortName):
    serialPort = serial.Serial(port= serialPortName, baudrate = baudRate, timeout=0, rtscts=True)
    # print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))
    waitForArduino(serialPort)
    return serialPort


def recvLikeArduino(serialPort):
    global startMarker, endMarker, dataStarted, dataBuf, messageComplete

    while serialPort.inWaiting() > 0 and messageComplete == False:
        x = serialPort.read().decode("utf-8")
        
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


def waitForArduino(serialPort):
    msg = ""
    while msg.find("READY") == -1:
        msg = recvLikeArduino(serialPort)


def sendToArduino(serialPort, stringToSend):
    global startMarker, endMarker

    stringWithMarkers = startMarker + stringToSend + endMarker
    serialPort.write(stringWithMarkers.encode('utf-8'))


if __name__ == "__main__":
    s = setupSerial(115200, "/dev/ttyACM0")
    print("arduino ready")
    while True:
        try:
            sendToArduino(s, "0")
            print("sent message to arduino")
            time.sleep(1)
            sendToArduino(s, "53")
            print("sent message to arduino")
            time.sleep(1)
        except KeyboardInterrupt:
            s.close()
            print("done...")
            break
