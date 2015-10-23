#!/usr/bin/python

import serial
import RPi.GPIO as GPIO

from reverseProxied import ReverseProxied

from flask import render_template
from flask import Flask
from flask import request
app = Flask(__name__)
app.config['DEBUG'] = True

app.wsgi_app = ReverseProxied(app.wsgi_app)

import datetime
from time import sleep

#from pprint import pformat

def getSystemTime():
    d = datetime.datetime.now()
    return {'day': d.isoweekday(), 'hour': d.hour, 'minute': d.minute}

def getXV25Time():
    ser = serial.Serial('/dev/ttyACM0', 921600, timeout=1)
    ser.write("GetTime\r\n".encode())
    answer = ser.read(4096) # Read answer
    lines = answer.decode().splitlines()
    date = lines[1]
    days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
    d = days.index(date.split()[0])
    h = int(date.split()[1].split(':')[0])
    m = int(date.split()[1].split(':')[1])
    ser.close()
    return  {'day': d, 'hour': h, 'minute': m}

def updateTime():
    alimUSB(True)
    sysTime = getSystemTime();
    xv25Time = getXV25Time();
    isTimeOk = (sysTime['day'] == xv25Time['day']) and (sysTime['hour'] == xv25Time['hour']) and (abs(sysTime['minute']-xv25Time['minute']) < 2)
    if not isTimeOk:
        ser = serial.Serial('/dev/ttyACM0', 921600, timeout=1)
        cmd = "SetTime %d %d %d\r\n"%(sysTime['day'],sysTime['hour'],sysTime['minute'])
        ser.write(cmd.encode())
        ser.close()
    alimUSB(False)

def setSchedule(on,day,hour,minute,activated):
    ser = serial.Serial('/dev/ttyACM0', 921600, timeout=1)
    enabled = "OFF"
    if on:
        enabled = "ON"
    typec = "None"
    if activated:
        typec = "House"
    cmd = "SetSchedule %d %d %d %s %s\r\n"%(int(day),int(hour),int(minute),typec,enabled)
    ser.write(cmd.encode())
    answer = ser.read(4096)
    ser.close()

def getSchedule():
    # Open serial port on robot
    ser = serial.Serial('/dev/ttyACM0', 921600, timeout=1)
 
    ser.write("GetSchedule\r\n".encode()) # Send clean command
    answer = ser.read(4096) # Read answer
    lines = answer.decode().splitlines()
    ser.close()
    ScheduleEnable = lines[1].split()[2] == 'Enabled'
    days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
    result = [{'ScheduleEnable': ScheduleEnable}]
    for i in range(2,9):
        line = lines[i]
        d = days.index(line.split()[0])
        h = line.split()[1].split(':')[0]
        m = line.split()[1].split(':')[1]
        e = line.split()[2] == 'H'
        result.append({'day': d, 'hour': h, 'minute': m, 'enabled': e})
    return result

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

def setupUSB():
    GPIO.setwarnings(False)
    # use P1 header pin numbering convention
    GPIO.setmode(GPIO.BCM)
 
    # Set up the GPIO channels
    GPIO.setup(17, GPIO.OUT)

def alimUSB(value):
    # Output to pin 17
    if value:
        GPIO.output(17, GPIO.HIGH)
    else:
        GPIO.output(17, GPIO.LOW)
    sleep(2)

def isChecked(value):
    if value:
        return 'checked'
    else:
        return ''

@app.before_first_request
def initialize():
    setupUSB()
    updateTime()

@app.route("/")
def index():
    alimUSB(True)
    s = getSchedule()
    alimUSB(False)
    return render_template('index.html',
            ScheduleEnable=isChecked(s[0]['ScheduleEnable']),
            lundih=s[2]['hour'],
            lundim=s[2]['minute'],
            lundie=isChecked(s[2]['enabled']),
            mardih=s[3]['hour'],
            mardim=s[3]['minute'],
            mardie=isChecked(s[3]['enabled']),
            mercredih=s[4]['hour'],
            mercredim=s[4]['minute'],
            mercredie=isChecked(s[4]['enabled']),
            jeudih=s[5]['hour'],
            jeudim=s[5]['minute'],
            jeudie=isChecked(s[5]['enabled']),
            vendredih=s[6]['hour'],
            vendredim=s[6]['minute'],
            vendredie=isChecked(s[6]['enabled']),
            samedih=s[7]['hour'],
            samedim=s[7]['minute'],
            samedie=isChecked(s[7]['enabled']),
            dimancheh=s[1]['hour'],
            dimanchem=s[1]['minute'],
            dimanchee=isChecked(s[1]['enabled'])
            )
@app.route("/sendschedule", methods=['POST'])
def sendschedule():
    #t = pformat(request.form)
    scheduleenable = 'scheduleenable' in request.form
    lundih = request.form['lundih']
    lundim = request.form['lundim']
    lundie = 'lundie' in request.form
    mardih = request.form['mardih']
    mardim = request.form['mardim']
    mardie = 'mardie' in request.form
    mercredih = request.form['mercredih']
    mercredim = request.form['mercredim']
    mercredie = 'mercredie' in request.form
    jeudih = request.form['jeudih']
    jeudim = request.form['jeudim']
    jeudie = 'jeudie' in request.form
    vendredih = request.form['vendredih']
    vendredim = request.form['vendredim']
    vendredie = 'vendredie' in request.form
    samedih = request.form['samedih']
    samedim = request.form['samedim']
    samedie = 'samedie' in request.form
    dimancheh = request.form['dimancheh']
    dimanchem = request.form['dimanchem']
    dimanchee = 'dimanchee' in request.form
    alimUSB(True)
    setSchedule(True,1,lundih,lundim,lundie)
    setSchedule(True,2,mardih,mardim,mardie)
    setSchedule(True,3,mercredih,mercredim,mercredie)
    setSchedule(True,4,jeudih,jeudim,jeudie)
    setSchedule(True,5,vendredih,vendredim,vendredie)
    setSchedule(True,6,samedih,samedim,samedie)
    setSchedule(scheduleenable,0,dimancheh,dimanchem,dimanchee)
    alimUSB(False)
    return render_template('ok.html')

@app.route("/startclean")
def startClean():
    alimUSB(True)
    sendClean()
    alimUSB(False)
    return "C'est parti !"

if __name__ == "__main__":
    app.run(host="0.0.0.0")
