#!/usr/bin/python
#
# install in cron:
# */5 * * * * /root/xv25ext/syncstoprpi.py
#

import serial

from crontab import CronTab

import datetime

def getSystemTime():
    d = datetime.datetime.now()
    return {'day': d.isoweekday(), 'hour': d.hour, 'minute': d.minute}

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

def getTodaySchedule():
    today = getSystemTime()
    allSchedules = getSchedule()
    if allSchedules[0]['ScheduleEnable']:
        for i in allSchedules:
            if 'day' in i and i['enabled'] and i['day'] == today['day']:
                return { 'hour': i['hour'], 'minute': i['minute']}

def resetCronHalt():
    cron   = CronTab()
    iter = cron.find_command('hardreboot.sh')
    for job in list(iter): 
        cron.remove(job)
    cron.write()

def getStopTime(hour,minute):
    scheduletime = datetime.datetime(14, 2, 22, int(hour), int(minute))
    delta = datetime.timedelta(minutes=2)
    stoptime = scheduletime - delta
    return (stoptime.hour,stoptime.minute)

def setCronHalt(hour,minute):
    cron   = CronTab()
    iter = cron.find_command('hardreboot.sh')
    for job in list(iter):
        cron.remove(job)
    job  = cron.new(command='/root/xv25ext/hardreboot.sh')
    job.minute.on(int(minute))
    job.hour.on(int(hour))
    cron.write()

if __name__ == "__main__":
    time = getTodaySchedule()
    if time:
        stoptime = getStopTime(time['hour'],time['minute'])
        setCronHalt(stoptime[0],stoptime[1])
    else:
        resetCronHalt()
