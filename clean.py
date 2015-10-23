#!/usr/bin/python
import serial
import RPi.GPIO as GPIO
 
def sendClean():
    # Open serial port on robot
    ser = serial.Serial('/dev/ttyACM0', 921600, timeout=1)
 
    # Ask clean until robot answer unplug USB
    while True:
        ser.write("Clean\r\n".encode()) # Send clean command
        ser.write("GetErr\r\n".encode()) # Send get error command
        answer = ser.read(4096) # Read answer
 
        # test if robot return 220 : you need remove USB cable
        for i in range(len(answer)):
            if answer[i:i+3] == b'220':
                return
 
def reboot():
    # use P1 header pin numbering convention
    GPIO.setmode(GPIO.BCM)
 
    # Set up the GPIO channels
    GPIO.setup(17, GPIO.OUT)
 
    # Output to pin 17
    GPIO.output(17, GPIO.HIGH)
 
if __name__ == "__main__":
    sendClean()
    reboot()
