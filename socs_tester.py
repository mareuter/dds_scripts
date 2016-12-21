from SALPY_scheduler import *
import time

sal = SAL_scheduler()
sal.setDebugLevel(0)

def send_topic(func, topic, message_success, message_failure):
    rcode = func(topic)
    if rcode == 0:
        print(message_success)
    else:
        print(message_failure)

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

sal.putSample_schedulerConfig(topic_schedulerConfig)
sal.putSample_driverConfig(topic_driverConfig)
sal.putSample_obsSiteConfig(topic_obsSiteConfig)
sal.putSample_telescopeConfig(topic_telescopeConfig)
sal.putSample_domeConfig(topic_domeConfig)
sal.putSample_rotatorConfig(topic_rotatorConfig)
sal.putSample_cameraConfig(topic_cameraConfig)
sal.putSample_slewConfig(topic_slewConfig)
sal.putSample_opticsLoopCorrConfig(topic_opticsLoopCorrConfig)
sal.putSample_parkConfig(topic_parkConfig)

for i in range(4):
    topic_generalPropConfig.prop_id = i + 1
    rcode = sal.putSample_generalPropConfig(topic_generalPropConfig)
    if rcode == 0:
        print("Proposal config {} sent".format(topic_generalPropConfig.prop_id))

print("Configuration sent")
print("Retrieving fields")

field_set = []
fields_from_dds = 0
end_fields = False
while True:
    rcode = sal.getNextSample_field(topicField)
    if topicField.ID == 0:
        continue
    if rcode == 0 and topicField.ID == -1:
        if end_fields:
            break
        else:
            end_fields = True
            continue
    field_set.append((topicField.ID, topicField.fov, topicField.ra, topicField.dec,
                      topicField.gl, topicField.gb, topicField.el, topicField.eb))
    fields_from_dds += 1
    time.sleep(0.00001)

print("Retrieved {} fields".format(fields_from_dds))

sal.salShutdown()
