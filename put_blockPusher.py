import numpy
import time
import sys

from SALPY_scheduler import *

START_TIME = "01/01/2022 19:00:00"
SIM_LENGTH = 1
DAYS_IN_YEAR = 2
VISIT_TIME = 40
SECONDS_IN_NIGHT = 160  # 10 * 60 * 60
SECONDS_IN_FULL_DAY = 360  # 24 * 60 * 60

USE_SAME_BLOCK = False

try:
    start_date = sys.argv[1]
except IndexError:
    start_date = START_TIME

start_seconds = time.mktime(time.strptime(start_date, "%m/%d/%Y %H:%M:%S"))

mgr = SAL_scheduler()
mgr.setDebugLevel(0)

mydata = scheduler_blockPusherC()
mgr.salTelemetryPub("scheduler_blockPusher")

# Setup data, using same image all the time
mydata.timestamp = int(start_seconds)

image = numpy.ones(len(mydata.block), dtype=numpy.float64)
for i, v in enumerate(image.tolist()):
    mydata.block[i] = v

begin_time = time.time()
count = 0
for i in xrange(int(round(SIM_LENGTH * DAYS_IN_YEAR))):
    print(i)
    end_of_night = mydata.timestamp + SECONDS_IN_NIGHT
    while mydata.timestamp <= end_of_night:
        print(mydata.timestamp)
        if not USE_SAME_BLOCK:
            for i, v in enumerate(image.tolist()):
                mydata.block[i] = v
        mgr.putSample_blockPusher(mydata)
        count += 1
        mydata.timestamp += VISIT_TIME
    if mydata.timestamp > end_of_night:
        mydata.timestamp = end_of_night
    # Run time to next night
    mydata.timestamp += (SECONDS_IN_FULL_DAY - SECONDS_IN_NIGHT)

mydata.timestamp = -1
mgr.putSample_blockPusher(mydata)

end_time = time.time()
diff_time = end_time - begin_time
print("Number of messages sent = {}".format(count))
print("Total time: {} seconds".format(diff_time))

mgr.salShutdown()
