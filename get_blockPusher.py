import sys

from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.setDebugLevel(0)
mydata = scheduler_blockPusherC()

mgr.salTelemetrySub("scheduler_blockPusher")

import datetime

count = 0
try:
    while True:
        scode = mgr.getNextSample_blockPusher(mydata)
        if scode == 0 and mydata.timestamp != 0:
            print("{}".format(datetime.datetime.fromtimestamp(mydata.timestamp).isoformat()))
	    image = mydata.block
            print("Image size: {}".format(len(image)))
            count += 1

except KeyboardInterrupt:
    mgr.salShutdown()
    print("")
    print("Number of messages received = {}".format(count))
    sys.exit(0)


