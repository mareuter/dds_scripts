import os
import sys
import time

try:
    delay = float(sys.argv[1])
except IndexError:
    delay = 1

from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.setDebugLevel(0)

mydata = scheduler_interestedProposalC()
mgr.salTelemetryPub("scheduler_interestedProposal")
time.sleep(1)

mydata.pairNumber = 2
mydata.proposalId = 1001
mydata.targetId = 3004
mydata.targetProposalRankValue = 0.10
mydata.targetRankPosition = 1

for i in range(10):
    mydata.subSequenceNumber = i+1
    mgr.putSample_interestedProposal(mydata)
    time.sleep(delay)

mgr.salShutdown()


