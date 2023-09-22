# nastavenie baudrate 500000 cez cmd line : stty -F /dev/ttyAMA0 500000

import time
import serial
import RPi.GPIO as GPIO			# GPIO control module

port = serial.Serial()         # create a serial port object
port.baudrate = 500000        # baud rate, in bits/second
port.port = "/dev/ttyAMA0"     # this is whatever port your are using
port.timeout = 0.001
port.open()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)	        # Set GPIO mode
tx = GPIO.HIGH			# High for TX mode
rx = GPIO.LOW			# Low for RX mode
directionPin = 18		# GPIO pin connected to Enable pins on buffer
GPIO.setup(directionPin, GPIO.OUT)	# Configure pin for output



def test ():     #otestuje vsetky serva od ID=0 az po ID=12, ak su vsetky OK, navrati hodnotu 1 , inak navrati 0
    status = 1
    for index in range (0,13):
        GPIO.output(directionPin, tx)	# set the direction pin
        time.sleep(0.0002)
	checksum = 255 - ((index + 1 + 2)%256)	# calculate the checksum	
	outData = chr(0xFF)+chr(0xFF)+chr(index)+chr(0x02)+chr(1)+chr(checksum)	# build a string with the first part
	port.write(outData)	# write it out of the serial port
	time.sleep(0.0002)

	port.flushInput()
	GPIO.output(directionPin, rx)	# set the direction pin
	time.sleep(0.0004)
	
	h1 = port.read()   # 0xff, used to make sure the servo responds
	h2 = port.read()   # 0xff, not used for anything
	origin = port.read()   # Origin ID
	length = port.read() 	# Length of data payload
	error = port.read()  # read the error data, was being tossed
	checksum = port.read()	# append the payload to the list

	    
	if (error!=chr(0) or h1 !=chr(255) or h2!=chr(255) or length!=chr(2) or origin!=chr(index)):
            print (str(index)+". servo ERROR ! :")
            if error== str(2):
                print("Angle limit!")
            if error== str(4):
                print("Overheating!")
            if error== str(8):
                print("Range!")
            if error== str(16):
                print("Checksum!")
            if error== str(32):
                print("Overload!")
            if error== str(64):
                print("Instruction!")

            status = 0
     
    return status
         
	        
        
def positionRead (index):       # funkcia navrati status a aktualnu poziciu
    status = 1                  # ak nacitanie pozicie prebehne OK, status=1, inak status=0  
    position=500                # default value
    port.flushOutput()
    GPIO.output(directionPin, tx)		# Set to TX mode
    time.sleep(0.0002)
    checksum = 255 - ((6 + index + 36 + 2)%256)	# calculate the checksum	
    outData = chr(0xFF)+chr(0xFF)+chr(index)+chr(0x04)+chr(2)+chr(36)+chr(2)+chr(checksum)	# build a string with the first part
    port.write(outData)	# write it out of the serial port
    time.sleep(0.0002)
    GPIO.output(directionPin, rx)		# Set to RX mode
    port.flushInput()
    time.sleep(0.0004)

        
    h1 = port.read()   # 0xff, used to make sure the servo responds	#
    h2 = port.read()   # 0xff, not used for anything
    origin = port.read()   # Origin ID
    length = port.read()	# Length of data payload
    error = port.read()   # read the error data, was being tossed   
    data_1 = port.read()
    data_2 = port.read()    
    
    if (error!=chr(0) or h1 !=chr(255) or h2!=chr(255) or length!=chr(4) or origin!=chr(index)):
        print (str(index)+". servo ERROR !")
        status = 0
    else:
        position = ((ord(data_2)<<8)|ord(data_1))
        status = 1

    output = [status, position]
    return output


def positionSet (index,position):  # nastavenie pozadovanej pozicie, ak je yapis do registra uspesny, navrati status=1, ak nie status=0
    GPIO.output(directionPin, tx)		# Set to TX mode
    time.sleep(0.0002)
    H_byte = position>>8
    L_byte = position%256
    checksum = 255-((index+5+3+30+L_byte+H_byte)%256)    # calculate checksum, same as ~(sum(data))  
    outputdata = chr(0xFF)+chr(0xFF)+chr(index)+chr(5)+chr(3)+chr(30)+chr(L_byte)+chr(H_byte)+chr(checksum)
    port.write(outputdata)	# Write the first part of the protocol
    time.sleep(0.003)

    status = 1                  # ak nastavenie pozicie prebehne OK, status=1, inak status=0  
    port.flushOutput()
    checksum = 255 - ((6 + index + 30 + 2)%256)	# calculate the checksum	
    outData = chr(0xFF)+chr(0xFF)+chr(index)+chr(0x04)+chr(2)+chr(30)+chr(2)+chr(checksum)	# build a string with the first part
    port.write(outData)	# write it out of the serial port
    time.sleep(0.0002)
    GPIO.output(directionPin, rx)		# Set to RX mode
    port.flushInput()
    time.sleep(0.0004)

    h1 = port.read()   # 0xff, used to make sure the servo responds	#
    h2 = port.read()   # 0xff, not used for anything
    origin = port.read()   # Origin ID
    length = port.read()	# Length of data payload
    error = port.read()   # read the error data, was being tossed   
    data_1 = port.read()
    data_2 = port.read()    
        
    if (error!=chr(0) or h1 !=chr(255) or h2!=chr(255) or length!=chr(4) or origin!=chr(index)):
        status = 0
    else:
        goal_position = ((ord(data_2)<<8)|ord(data_1))
        if goal_position==position:
            status=1
        else:
            status=0

    if status==0:
        print ("Servo " +str(index)+" - zapis cielovej pozicie neuspesny !")

    return status
	
def speedSet (index,speed): #nastavime rychlost pohybu serva a vratime hodnotu status=1 ak zapis bol uspesny 
    GPIO.output(directionPin, tx)		# Set to TX mode
    port.flushOutput()
    time.sleep(0.0002)
    H_byte = speed>>8
    L_byte = speed%256
    checksum = 255-((index+5+3+32+L_byte+H_byte)%256)    # calculate checksum, same as ~(sum(data))  
    outputdata = chr(0xFF)+chr(0xFF)+chr(index)+chr(5)+chr(3)+chr(32)+chr(L_byte)+chr(H_byte)+chr(checksum)
    port.write(outputdata)	# Write the first part of the protocol
    time.sleep(0.003)

    status = 1                  # ak nastavenie pozicie prebehne OK, status=1, inak status=0  
    port.flushOutput()
    checksum = 255 - ((6 + index + 32 + 2)%256)	# calculate the checksum	
    outData = chr(0xFF)+chr(0xFF)+chr(index)+chr(0x04)+chr(2)+chr(32)+chr(2)+chr(checksum)	# build a string with the first part
    port.write(outData)	# write it out of the serial port
    time.sleep(0.0002)
    GPIO.output(directionPin, rx)		# Set to RX mode
    port.flushInput()
    time.sleep(0.0004)

    h1 = port.read()   # 0xff, not used for anything
    h2 = port.read()   # 0xff, not used for anything
    origin = port.read()   # Origin ID
    length = port.read()	# Length of data payload
    error = port.read()   # read the error data, was being tossed   
    data_1 = port.read()
    data_2 = port.read()    
        
    if (error!=chr(0) or h1 !=chr(255) or h2!=chr(255) or length!=chr(4) or origin!=chr(index)):
        status = 0
    else:
        speed_from_register = ((ord(data_2)<<8)|ord(data_1))
        if speed==speed_from_register:
            status = 1
        else:
            status = 0
       
    return status

def servoDefault ():
    pozicie=[500,520,2050,2050,1668,1000,1200,1900,2500,3050,2900,2200,1400]
    
    for i in range (0,13):
        j=0
        while ((speedSet(i,40) != 1)  and (j < 3)):  # Nastavenie rychlosti. Slucka sa ukonci po 3 opakovaniach, alebo po uspesnom zapise rychlosti
            j=j+1

        j=0
        status=0
        while ((status != 1)  and (j < 3)):  # Nastavenie pozicie. Slucka sa ukonci po 3 opakovaniach, alebo po uspesnom zapise pozicie
            status=positionSet(i,pozicie[i])
            j=j+1
              
    print "Pripraveny vo vychodiskovej pozicii."
    time.sleep(1)


    
def bussy(index):           #zisti, ci dany motor prave vykonava pohyb, ak vykonava, tak bussy=1, inak bussy=0
    status = 1                  # ak nacitanie stavu bussy prebehne OK, status=1, inak status=0  
    port.flushOutput()
    GPIO.output(directionPin, tx)		# Set to TX mode
    time.sleep(0.0002)
    checksum = 255 - ((6 + index + 46 + 1)%256)	# calculate the checksum	
    outData = chr(0xFF)+chr(0xFF)+chr(index)+chr(0x04)+chr(2)+chr(46)+chr(1)+chr(checksum)	# build a string with the first part
    port.write(outData)	# write it out of the serial port
    time.sleep(0.0002)
    GPIO.output(directionPin, rx)		# Set to RX mode
    port.flushInput()
    time.sleep(0.0004)

        
    h1 = port.read()   # 0xff, used to make sure the servo responds	#
    h2 = port.read()   # 0xff, not used for anything
    origin = port.read()   # Origin ID
    length = port.read()	# Length of data payload
    error = port.read()   # read the error data, was being tossed   
    bussy = port.read()
        
    if (error!=chr(0) or h1 !=chr(255) or h2!=chr(255) or length!=chr(3) or origin!=chr(index) or ((bussy!=chr(0)) and (bussy!=chr(1)))):
        print (str(index)+". servo ERROR ! :")
        status = 0
        bussy='0'
    
        
    output = [status, ord(bussy)]
    return output
#****************************************************************************
def PIDset (index,P,I,D): #nastavime parametre PID regulatora polohy servomotora
    GPIO.output(directionPin, tx)		# Set to TX mode
    port.flushOutput()
    time.sleep(0.0002)
    checksum = 255-((index+4+3+28+P)%256)    # calculate checksum, same as ~(sum(data))  
    outputdata = chr(0xFF)+chr(0xFF)+chr(index)+chr(4)+chr(3)+chr(28)+chr(P)+chr(checksum)
    port.write(outputdata)	
    time.sleep(0.003)

    port.flushOutput()
    time.sleep(0.0002)
    checksum = 255-((index+4+3+27+I)%256)    # calculate checksum, same as ~(sum(data))  
    outputdata = chr(0xFF)+chr(0xFF)+chr(index)+chr(4)+chr(3)+chr(27)+chr(I)+chr(checksum)
    port.write(outputdata)	
    time.sleep(0.003)

    port.flushOutput()
    time.sleep(0.0002)
    checksum = 255-((index+4+3+26+D)%256)    # calculate checksum, same as ~(sum(data))  
    outputdata = chr(0xFF)+chr(0xFF)+chr(index)+chr(4)+chr(3)+chr(26)+chr(D)+chr(checksum)
    port.write(outputdata)	
    time.sleep(0.003)

    
#******************************************************************************
