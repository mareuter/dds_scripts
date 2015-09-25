import sys

from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.setDebugLevel(0)
mydata = scheduler_timeHandlerC()

mgr.salTelemetrySub("scheduler_timeHandler")

import time

count = 0
try:
    while True:
        scode = mgr.getNextSample_timeHandler(mydata)
        if scode == 0 and mydata.timestamp != 0:
            print("{}".format(time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(mydata.timestamp))))
            count += 1

except KeyboardInterrupt:
    mgr.salShutdown()
    print("")
    print("Number of messages received = {}".format(count))
    sys.exit(0)


