from SALPY_scheduler import *
import time

def recv_topic(function, topic, message_success, message_failure, extra_message=None):
    waitconfig = True
    lastconfigtime = time.time()
    while waitconfig:
        scode = function(topic)
        if scode == 0:
            print(message_success)
            if extra_message is not None:
                print("{} = {}".format(extra_message[0], getattr(topic, extra_message[1])))
            lastconfigtime = time.time()
            waitconfig = False
        else:
            tf = time.time()
            if (tf - lastconfigtime > 10.0):
                print(message_failure)
                waitconfig = False

sal = SAL_scheduler()
sal.setDebugLevel(0)

# Initialize all topics
topic_schedulerConfig = scheduler_schedulerConfigC()
topic_driverConfig = scheduler_driverConfigC()
topic_obsSiteConfig = scheduler_obsSiteConfigC()
topic_telescopeConfig = scheduler_telescopeConfigC()
topic_domeConfig = scheduler_domeConfigC()
topic_rotatorConfig = scheduler_rotatorConfigC()
topic_cameraConfig = scheduler_cameraConfigC()
topic_slewConfig = scheduler_slewConfigC()
topic_opticsLoopCorrConfig = scheduler_opticsLoopCorrConfigC()
topic_parkConfig = scheduler_parkConfigC()
topic_generalPropConfig = scheduler_generalPropConfigC()
topicTime = scheduler_timeHandlerC()
topicObservatoryState = scheduler_observatoryStateC()
topic_cloud = scheduler_cloudC()
topic_seeing = scheduler_seeingC()
topicObservation = scheduler_observationC()
topicField = scheduler_fieldC()
topicTarget = scheduler_targetC()
topicFilterSwap = scheduler_filterSwapC()
topicInterestedProposal = scheduler_interestedProposalC()

# Initialize all subs and pubs

sal.salTelemetrySub("scheduler_schedulerConfig")
sal.salTelemetrySub("scheduler_driverConfig")
sal.salTelemetrySub("scheduler_obsSiteConfig")
sal.salTelemetrySub("scheduler_telescopeConfig")
sal.salTelemetrySub("scheduler_domeConfig")
sal.salTelemetrySub("scheduler_rotatorConfig")
sal.salTelemetrySub("scheduler_cameraConfig")
sal.salTelemetrySub("scheduler_slewConfig")
sal.salTelemetrySub("scheduler_opticsLoopCorrConfig")
sal.salTelemetrySub("scheduler_parkConfig")
sal.salTelemetrySub("scheduler_generalPropConfig")
sal.salTelemetrySub("scheduler_timeHandler")
sal.salTelemetrySub("scheduler_observatoryState")
sal.salTelemetrySub("scheduler_cloud")
sal.salTelemetrySub("scheduler_seeing")
sal.salTelemetrySub("scheduler_observation")
sal.salTelemetryPub("scheduler_field")
sal.salTelemetryPub("scheduler_target")
sal.salTelemetryPub("scheduler_filterSwap")
sal.salTelemetryPub("scheduler_interestedProposal")

print("Scheduler Ready")

recv_topic(sal.getNextSample_schedulerConfig, topic_schedulerConfig,
           "scheduler Config received", "scheduler Config timeout")
recv_topic(sal.getNextSample_driverConfig, topic_driverConfig,
           "driver Config received", "driver Config timeout")
recv_topic(sal.getNextSample_telescopeConfig, topic_telescopeConfig,
           "telescope Config received", "telescope Config timeout")
recv_topic(sal.getNextSample_domeConfig, topic_domeConfig,
           "dome Config received", "dome Config timeout")
recv_topic(sal.getNextSample_rotatorConfig, topic_rotatorConfig,
           "rotator Config received", "rotator Config timeout")
recv_topic(sal.getNextSample_cameraConfig, topic_cameraConfig,
           "camera Config received", "camera Config timeout")
recv_topic(sal.getNextSample_slewConfig, topic_slewConfig,
           "slew Config received", "slew Config timeout")
recv_topic(sal.getNextSample_opticsLoopCorrConfig, topic_opticsLoopCorrConfig,
           "opticsLoopCorr Config received", "opticsLoopCorr Config timeout")
recv_topic(sal.getNextSample_parkConfig, topic_parkConfig,
           "park Config received", "park Config timeout")
recv_topic(sal.getNextSample_generalPropConfig, topic_generalPropConfig,
           "generalProp Config received", "generalProp Config timeout", extra_message=("Prop Id", "prop_id"))

print("Transferring fields")

topicField.ID = -1
counter = 0
rcode = sal.putSample_field(topicField)
if rcode == 0:
    counter += 1
for i in range(5292):
    topicField.ID = i + 1
    rcode = sal.putSample_field(topicField)
    if rcode == 0:
        counter += 1
topicField.ID = -1
rcode = sal.putSample_field(topicField)
if rcode == 0:
    counter += 1

print("{} Fields transferred".format(counter))
print("Starting target cycle")

targets_sent = 1
waittime = True
lasttimetime = time.time()
while waittime:
    scode = sal.getNextSample_timeHandler(topicTime)
    if scode == 0:
        lasttimetime = time.time()
        topicTarget.targetId = targets_sent
        sal.putSample_target(topicTarget)
        print("Sent target {}".format(topicTarget.targetId))
        targets_sent += 1

        waitobservation = True
        lastobstime = time.time()
        while waitobservation:
            lastobstime = time.time()
            scode = sal.getNextSample_observation(topicObservation)
            if scode == 0:
                print("Received observation {} [{}]".format(topicObservation.observationId,
                                                            topicObservation.targetId))
                waitobservation = False
            else:
                to = time.time()
                if (to - lastobstime > 10.0):
                    waitobservation = False
    else:
        tc = time.time()
        if (tc - lasttimetime) > 10.0:
            waittime = False

sal.salShutdown()
