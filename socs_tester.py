from __future__ import print_function
from datetime import datetime
import os
from SALPY_scheduler import *
import sys
import time

TIME_INCREMENT = 40
NUM_OBSERVATIONS = 10000
try:
    NUM_OBSERVATIONS = int(sys.argv[1])
except IndexError:
    pass

unix_start = datetime(1970, 1, 1)
time_start = (datetime.utcnow() - unix_start).total_seconds()

sal = SAL_scheduler()
sal.setDebugLevel(0)

def send_topic(func, topic, message_success, message_failure, extra_item=None):
    fail_counter = 0
    while True:
        rcode = func(topic)
        if rcode == 0:
            if fail_counter:
                print()
            message = []
            if "{}" in message_success:
                message.append(message_success.format(getattr(topic, extra_item)))
            else:
                message.append(message_success)
            message.append("with {} errors.".format(fail_counter))
            print(" ".join(message))
            break
        else:
            if fail_counter == 0:
                print(message_failure)
            elif fail_counter % 50 == 0:
                print(".", end="")
            fail_counter += 1

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

sal.salTelemetryPub("scheduler_schedulerConfig")
sal.salTelemetryPub("scheduler_driverConfig")
sal.salTelemetryPub("scheduler_obsSiteConfig")
sal.salTelemetryPub("scheduler_telescopeConfig")
sal.salTelemetryPub("scheduler_domeConfig")
sal.salTelemetryPub("scheduler_rotatorConfig")
sal.salTelemetryPub("scheduler_cameraConfig")
sal.salTelemetryPub("scheduler_slewConfig")
sal.salTelemetryPub("scheduler_opticsLoopCorrConfig")
sal.salTelemetryPub("scheduler_parkConfig")
sal.salTelemetryPub("scheduler_generalPropConfig")
sal.salTelemetryPub("scheduler_timeHandler")
sal.salTelemetryPub("scheduler_observatoryState")
sal.salTelemetryPub("scheduler_cloud")
sal.salTelemetryPub("scheduler_seeing")
sal.salTelemetryPub("scheduler_observation")
sal.salTelemetrySub("scheduler_field")
sal.salTelemetrySub("scheduler_target")
sal.salTelemetrySub("scheduler_filterSwap")
sal.salTelemetrySub("scheduler_interestedProposal")

print("SOCS Ready")

send_topic(sal.putSample_schedulerConfig, topic_schedulerConfig,
           "scheduler Config sent", "scheduler Config publish failed")
send_topic(sal.putSample_driverConfig, topic_driverConfig,
           "driver Config sent", "driver Config publish failed")
send_topic(sal.putSample_obsSiteConfig, topic_obsSiteConfig,
           "obsSite Config sent", "obsSite Config publish failed")
send_topic(sal.putSample_telescopeConfig, topic_telescopeConfig,
           "telescope Config sent", "telescope Config publish failed")
send_topic(sal.putSample_domeConfig, topic_domeConfig,
           "dome Config sent", "dome Config publish failed")
send_topic(sal.putSample_rotatorConfig, topic_rotatorConfig,
           "rotator Config sent", "rotator Config publish failed")
send_topic(sal.putSample_cameraConfig, topic_cameraConfig,
           "camera Config sent", "camera Config publish failed")
send_topic(sal.putSample_slewConfig, topic_slewConfig,
           "slew Config sent", "slew Config publish failed")
send_topic(sal.putSample_opticsLoopCorrConfig, topic_opticsLoopCorrConfig,
           "opticsLoopCorr Config sent", "opticsLoopCorr Config publish failed")
send_topic(sal.putSample_parkConfig, topic_parkConfig,
           "park Config sent", "park Config publish failed")

for i in range(4):
    topic_generalPropConfig.prop_id = i + 1
    send_topic(sal.putSample_generalPropConfig, topic_generalPropConfig,
               "generalProp Config {} sent", "generalProp Config publish failed",
               extra_item="prop_id")

print("Configuration sent")
print("Retrieving fields")

field_set = []
good_fields_from_dds = 0
bad_fields_from_dds = 0
end_fields = False
while True:
    rcode = sal.getNextSample_field(topicField)
    if rcode == 0 and topicField.ID == -1:
        if end_fields:
            break
        else:
            end_fields = True
            continue
    if rcode == 0:
        field_set.append((topicField.ID, topicField.fov, topicField.ra, topicField.dec,
                          topicField.gl, topicField.gb, topicField.el, topicField.eb))
        good_fields_from_dds += 1
    else:
        bad_fields_from_dds += 1

print("Retrieved {} good fields".format(good_fields_from_dds))
print("Retrieved {} bad fields".format(bad_fields_from_dds))
print("Starting observation cycle")

topicTime.timestamp = time_start
for o in range(NUM_OBSERVATIONS):
    sal.putSample_timeHandler(topicTime)
    while True:
        rcode = sal.getNextSample_target(topicTarget)
        if rcode == 0:
            break
    print("Received target {}".format(topicTarget.targetId))
    topicObservation.observation_start_time = topicTime.timestamp
    topicObservation.targetId = topicTarget.targetId
    topicObservation.observationId = topicTarget.targetId
    sal.putSample_observation(topicObservation)
    print("Sent observation {}".format(topicObservation.observationId))

    topicTime.timestamp += TIME_INCREMENT

if good_fields_from_dds > 5292:
    with open("field_dump_{}.txt".format(datetime.now().strftime("%Y-%m-%d_%H:%M:%S")), 'w') as ofile:
        for field in field_set:
            ofile.write(str(field[0]) + os.linesep)

sal.salShutdown()
