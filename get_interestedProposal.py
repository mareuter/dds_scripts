import os
import sys

from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.setDebugLevel(1)
mydata = scheduler_interestedProposalC()

mgr.salTelemetrySub("scheduler_interestedProposal")

count = 1
while True:
    scode = mgr.getNextSample_interestedProposal(mydata)
    if scode == 0 and mydata.subSequenceNumber != 0:
        print("%d: %d" % (count, mydata.subSequenceNumber))
        count += 1

mgr.salShutdown()


