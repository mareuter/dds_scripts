from SALPY_scheduler import *
mgr = SAL_scheduler()
#mgr.setDebugLevel(0)
mgr.salTelemetryPub("scheduler_observation")
d = scheduler_observationC()
i = 0
while i < 5000:
    d.observationId = i
    mgr.putSample_observation(d)
    i += 1
