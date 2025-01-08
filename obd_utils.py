
import serial
import platform


def scanSerial():
    """Scan for available ports. Return a list of serial names."""
    available = []
    # Enable Bluetooth connection
    for i in range(10):
        try:
            s = serial.Serial("/dev/rfcomm" + str(i))
            available.append((str(s.port)))
            s.close()  # explicit close because of delayed GC in Python
        except serial.SerialException:
            pass
    # Enable USB connection
    for i in range(256):
        try:
            s = serial.Serial("/dev/ttyUSB" + str(i))
            available.append(s.portstr)
            s.close()  # explicit close because of delayed GC in Python
        except serial.SerialException:
            pass


    # Enable obdsim
    for i in range(256):
         try:  # scan Simulator
            s = serial.Serial("/dev/pts/" + str(i))
            available.append(s.portstr)
            s.close()  # explicit close because of delayed GC in Python
         except serial.SerialException:
             pass

    return available



