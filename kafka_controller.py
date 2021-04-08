from __future__ import unicode_literals

import logging
import typing

from kafka import KafkaConsumer, KafkaProducer

import NewSegmentationIsReadyEvent_pb2 as msg


EVENT_TOPIC = 'eventTopic'

log = logging.getLogger(__name__)


def connect_kafka_producer() -> KafkaProducer:
    try:
        producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
    except Exception as error:
        log.error("Producer connection failed", exc_info=error)
        raise
    log.info("Producer connection success")
    return producer


def publish_message(
        producer: KafkaProducer, topic_name: str, data: msg.NewSegmentationIsReadyEvent
) -> None:
    try:
        # key_bytes = bytes(str(key), encoding='utf-8')
        # value_bytes = bytes(str(value), encoding='utf-8')
        # print(data)

        # key=key_bytes, value=value_bytes)
        producer.send(topic_name, data.SerializeToString())
        producer.flush()
        log.info("Message successfully sent")
    except Exception as error:
        log.error("Failed to publish message", exc_info=error)


def get_message(consumer: KafkaConsumer) -> typing.List[typing.Any]:
    links = []
    for message in consumer:
        value = message.value
        link = msg.NewSegmentationIsReadyEvent()
        link.ParseFromString(value)
        log.info("Message successfully received: %s", link)
        # log.info(str(link))
        links.append(link)
        return links


def kafka_try_send() -> None:
    producer = connect_kafka_producer()
    consumer = KafkaConsumer(
        EVENT_TOPIC, bootstrap_servers=['localhost:9092'], auto_offset_reset='earliest'
    )

    segm = msg.NewSegmentationIsReadyEvent()

    segm.segmLink = "http://nowhere"
    segm.maskLink = "http://non-existent"
    segm.wineId = "1"

    # serialized = segm.SerializeToString()

    log.info("Sent event %s", segm)

    publish_message(producer, EVENT_TOPIC, segm)  # 'msg', str(serialized))
    get_message(consumer)


kafka_try_send()

# Test that the protobuf serialize and de-serialize methods are working fine
'''
def serialize_deserialize_test()
    segm = msg.Segmentation()
    segm2 = msg.Segmentation()

    segm.segm_link = "http://nowhere"
    segm.mask_link = "http://non-existent"
    segm.id = 1

    serialized = segm.SerializeToString()

    print(serialized)
    segm2.ParseFromString(serialized)
    print(segm2)
'''