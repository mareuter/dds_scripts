from SALPY_scheduler import *
mgr = SAL_scheduler()
mgr.salTelemetrySub("scheduler_observation")
d = scheduler_observationC()
i = 0
print("Starting loop")
while True:
    s = mgr.getNextSample_observation(d)
    if s == 0:
        print(i)
        i += 1
