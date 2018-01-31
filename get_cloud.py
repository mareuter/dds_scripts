from __future__ import print_function
import SALPY_scheduler
import sys
import time

def main():
    try:
        manager = SALPY_scheduler.SAL_scheduler()
        manager.setDebugLevel(0)
        manager.salTelemetrySub("scheduler_cloud")

        cloud = SALPY_scheduler.scheduler_cloudC()

        for i in range(100):
            print("Iteration {}".format(i))
            wait_cloud = True
            lastcloudtime = time.time()
            while wait_cloud:
                rcode = manager.getNextSample_cloud(cloud)
                if rcode == 0:
                    print(cloud.timestamp, cloud.cloud)
                    lastcloudtime = time.time()
                    wait_cloud = False
                else:
                    tf = time.time()
                    if tf - lastcloudtime > 10.0:
                        wait_cloud = False
                        print("Cloud timeout")
                        print(cloud.timestamp, cloud.cloud)

    except KeyboardInterrupt:
        manager.salShutdown()
        sys.exit(0)

if __name__ == '__main__':
    main()
