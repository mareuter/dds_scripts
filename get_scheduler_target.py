from __future__ import print_function
import SALPY_scheduler
import sys

if __name__ == '__main__':

    try:

        manager = SALPY_scheduler.SAL_scheduler()
        manager.setDebugLevel(0)
        manager.salTelemetrySub("scheduler_target")
        target = SALPY_scheduler.scheduler_targetC()

        while True:
            rcode = manager.getNextSample_target(target)
            if rcode == 0:
                print("Target: Id = {}, RA = {}, Dec = {}".format(target.targetId,
                                                                  target.ra, target.dec))
    except KeyboardInterrupt:
        manager.salShutdown()
        sys.exit(0)
