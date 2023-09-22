import time
import serial
import RPi.GPIO as GPIO  # GPIO control module

port = serial.Serial()  # create a serial port object
port.baudrate = 500000  # baud rate, in bits/second
port.port = "/dev/ttyAMA0"  # this is whatever port you are using
port.timeout = 0.001
port.open()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Set GPIO mode
tx = GPIO.HIGH  # High for TX mode
rx = GPIO.LOW  # Low for RX mode
directionPin = 18  # GPIO pin connected to Enable pins on buffer
GPIO.setup(directionPin, GPIO.OUT)  # Configure pin for output


def test():
    status = 1
    for index in range(0, 13):
        GPIO.output(directionPin, tx)  # set the direction pin
        time.sleep(0.0002)
        checksum = 255 - ((index + 1 + 2) % 256)  # calculate the checksum
        outData = (
            chr(0xFF)
            + chr(0xFF)
            + chr(index)
            + chr(0x02)
            + chr(1)
            + chr(checksum)
        )  # build a string with the first part
        port.write(outData)  # write it out of the serial port
        time.sleep(0.0002)

        port.flushInput()
        GPIO.output(directionPin, rx)  # set the direction pin
        time.sleep(0.0004)

        h1 = port.read()  # 0xff, used to make sure the servo responds
        h2 = port.read()  # 0xff, not used for anything
        origin = port.read()  # Origin ID
        length = port.read()  # Length of data payload
        error = port.read()  # read the error data, was being tossed
        checksum = port.read()  # append the payload to the list

        if (
            error != chr(0)
            or h1 != chr(255)
            or h2 != chr(255)
            or length != chr(2)
            or origin != chr(index)
        ):
            print(str(index) + ". servo ERROR ! :")
            if error == str(2):
                print("Angle limit!")
            if error == str(4):
                print("Overheating!")
            if error == str(8):
                print("Range!")
            if error == str(16):
                print("Checksum!")
            if error == str(32):
                print("Overload!")
            if error == str(64):
                print("Instruction!")

            status = 0

    return status


def positionRead(index):
    status = 1
    position = 500
    port.flushOutput()
    GPIO.output(directionPin, tx)  # Set to TX mode
    time.sleep(0.0002)
    checksum = 255 - ((6 + index + 36 + 2) % 256)  # calculate the checksum
    outData = (
        chr(0xFF)
        + chr(0xFF)
        + chr(index)
        + chr(0x04)
        + chr(2)
        + chr(36)
        + chr(2)
        + chr(checksum)
    )  # build a string with the first part
    port.write(outData)  # write it out of the serial port
    time.sleep(0.0002)
    GPIO.output(directionPin, rx)  # Set to RX mode
    port.flushInput()
    time.sleep(0.0004)

    h1 = port.read()  # 0xff, used to make sure the servo responds
    h2 = port.read()  # 0xff, not used for anything
    origin = port.read()  # Origin ID
    length = port.read()  # Length of data payload
    error = port.read()  # read the error data, was being tossed
    data_1 = port.read()
    data_2 = port.read()

    if (
        error != chr(0)
        or h1 != chr(255)
        or h2 != chr(255)
        or length != chr(4)
        or origin != chr(index)
    ):
        print(str(index) + ". servo ERROR !")
        status = 0
    else:
        position = ((ord(data_2) << 8) | ord(data_1))
        status = 1

    output = [status, position]
    return output


def positionSet(index, position):
    GPIO.output(directionPin, tx)  # Set to TX mode
    time.sleep(0.0002)
    H_byte = position >> 8
    L_byte = position % 256
    checksum = 255 - (
        (index + 5 + 3 + 30 + L_byte + H_byte) % 256
    )  # calculate checksum, same as ~(sum(data))
    outputdata = (
        chr(0xFF)
        + chr(0xFF)
        + chr(index)
        + chr(5)
        + chr(3)
        + chr(30)
        + chr(L_byte)
        + chr(H_byte)
        + chr(checksum)
    )
    port.write(outputdata)  # Write the first part of the protocol
    time.sleep(0.003)

    status = 1
    port.flushOutput()
    time.sleep(0.0002)
    checksum = 255 - (
        (6 + index + 30 + 2) % 256
    )  # calculate the checksum
    outData = (
        chr(0xFF)
        + chr(0xFF)
        + chr(index)
        + chr(0x04)
        + chr(2)
        + chr(30)
        + chr(2)
        + chr(checksum)
    )  # build a string with the first part
