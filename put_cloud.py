from __future__ import print_function
import SALPY_scheduler
import sys
import time

def main():
    try:
        manager = SALPY_scheduler.SAL_scheduler()
        manager.setDebugLevel(0)
        manager.salTelemetryPub("scheduler_cloud")

        cloud = SALPY_scheduler.scheduler_cloudC()

        counter = 1
        while True:
            cloud.timestamp = time.time()
            cloud.cloud = float(counter)
            manager.putSample_cloud(cloud)
            time.sleep(30)
            counter += 1

        manager.salShutdown()

    except KeyboardInterrupt:
        manager.salShutdown()
        sys.exit(0)

if __name__ == '__main__':
    main()
