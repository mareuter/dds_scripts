import sys

START_TIME = "05/24/2020 19:00:00"
SIM_LENGTH = 1
DAYS_IN_YEAR = 365
VISIT_TIME = 40
SECONDS_IN_NIGHT = 10 * 60 * 60
SECONDS_IN_FULL_DAY = 24 * 60 * 60

import time

try:
    start_date = sys.argv[1]
except IndexError:
    start_date = START_TIME

start_seconds = time.mktime(time.strptime(start_date, "%m/%d/%Y %H:%M:%S"))

from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.setDebugLevel(1)

mydata = scheduler_timeHandlerC()
mgr.salTelemetryPub("scheduler_timeHandler")

mydata.timestamp = int(start_seconds)

count = 0
for i in xrange(int(round(SIM_LENGTH * DAYS_IN_YEAR))):
    end_of_night = mydata.timestamp + SECONDS_IN_NIGHT
    while mydata.timestamp <= end_of_night:
	mgr.putSample_timeHandler(mydata)
        count += 1
	mydata.timestamp += VISIT_TIME
    if mydata.timestamp > end_of_night:
	mydata.timestamp = end_of_night
    # Run time to next night    
    mydata.timestamp += (SECONDS_IN_FULL_DAY - SECONDS_IN_NIGHT)

print("Number of messages sent = {}".format(count))
mgr.salShutdown()


