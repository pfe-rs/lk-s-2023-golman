import serial

s = serial.Serial("/dev/ttyACM0", 115200)

if __name__ == "__main__":
    s.setDTR(True)
    s.write(str.encode("Hello!"))
    s.close()
