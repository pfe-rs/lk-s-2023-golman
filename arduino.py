import serial
import time

startMarker = '<'
endMarker = '>'

dataStarted = False
dataBuf = ""
messageComplete = False


def setupSerial(baudRate: int, serialPortName: str):
    serialPort = serial.Serial(port= serialPortName, baudrate = baudRate, timeout=0, rtscts=True)
    # print("Serial port " + serialPortName + " opened  Baudrate " + str(baudRate))
    waitForArduino(serialPort)
    return serialPort


def recvLikeArduino(serialPort: serial.Serial):
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


def waitForArduino(serialPort: serial.Serial):
    msg = ""
    while msg.find("READY") == -1:
        msg = recvLikeArduino(serialPort)


def sendToArduino(serialPort: serial.Serial, stringToSend: str):
    global startMarker, endMarker

    stringWithMarkers = startMarker + stringToSend + endMarker
    serialPort.write(stringWithMarkers.encode('utf-8'))


if __name__ == "__main__":
    s = setupSerial(115200, "/dev/ttyACM0")
    print("arduino ready")
    time.sleep(3)
    print("keyboard enabled")
    while True:
        try:
            value = input("command> ")
            sendToArduino(s, value)
            print("sent message to arduino")
            # time.sleep(1.6)
            # sendToArduino(s, "200 0")
            # print("sent message to arduino")
            # time.sleep(1.6)
        except KeyboardInterrupt:
            s.close()
            print("done...")
            break
