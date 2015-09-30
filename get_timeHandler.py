import sys

from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.setDebugLevel(0)
mydata = scheduler_timeHandlerC()

mgr.salTelemetrySub("scheduler_timeHandler")

import datetime

count = 0
try:
    while True:
        scode = mgr.getNextSample_timeHandler(mydata)
        if scode == 0 and mydata.timestamp != 0:
            count += 1
            print("{}".format(datetime.datetime.fromtimestamp(mydata.timestamp).isoformat()))

except KeyboardInterrupt:
    mgr.salShutdown()
    print("")
    print("Number of messages received = {}".format(count))
    sys.exit(0)


