import logging
import time
import typing

import requests
from kafka import KafkaConsumer, KafkaProducer

import config
from new_wine_saved_message_sent_event_pb2 import NewWineSavedMessageSentEvent
from NewSegmentationIsReadyEvent_pb2 import NewSegmentationIsReadyEvent


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
    producer: KafkaProducer, topic_name: str, data: NewSegmentationIsReadyEvent
) -> None:
    try:
        # key_bytes = bytes(str(key), encoding='utf-8')
        # value_bytes = bytes(str(value), encoding='utf-8')
        # print(data)

        # key=key_bytes, value=value_bytes)
        producer.send(topic=topic_name, value=data.SerializeToString())
        producer.flush()
        log.info("Message successfully sent")
    except Exception as error:
        log.error("Failed to publish message", exc_info=error)


# TODO: determine the returned type
def get_message(consumer: KafkaConsumer) -> typing.List[typing.Any]:
    links = []
    for message in consumer:
        value = message.value
        link = NewSegmentationIsReadyEvent()
        link.ParseFromString(value)
        log.info("Message successfully received: %s", link)
        # log.info(str(link))
        links.append(link)
    return links


def get_wine_image_link(wine_id: str) -> str:
    r = requests.get(f'{config.CATALOG_POSITION_BY_ID_CONTROLLER}/{wine_id}')
    response_body = r.json()
    if r.status_code != 200:
        raise ValueError(f"Failed to get wine_id, got {r.status_code}: {response_body}")
    return response_body.get('link_to_wine')


def get_image_segmentation(image_link: str) -> typing.Dict[str, str]:
    r = requests.post(
        config.RECOMMENDATION_SEGMENTATION_ENDPOINT, json={'image': image_link}
    )
    response_body = r.json()
    if r.status_code != 200:
        raise ValueError(
            f"Failed to get image segmentation, got {r.status_code}: {response_body}"
        )
    return response_body


def create_segmentation_event(wine_id: str, link: str) -> NewSegmentationIsReadyEvent:
    segmentation_result = get_image_segmentation(link)
    segmentation_link = segmentation_result.get('segmentation')
    mask_link = segmentation_result.get('mask')

    segmentation = NewSegmentationIsReadyEvent()
    segmentation.segmLink = segmentation_link
    segmentation.maskLink = mask_link
    segmentation.wineId = wine_id

    return segmentation


def process_messages(consumer: KafkaConsumer, producer: KafkaProducer) -> None:
    for message in consumer:
        value = message.value
        msg = NewWineSavedMessageSentEvent()
        msg.ParseFromString(value)
        log.info("Received NewWineSavedMessageSentEvent: %s", msg)

        wine_id = msg.wineId
        wine_image_link = get_wine_image_link(wine_id)

        segmentation_event = create_segmentation_event(wine_id, wine_image_link)

        publish_message(
            producer,
            topic_name=config.NEW_SEGMENTATION_IS_READY_TOPIC,
            data=segmentation_event,
        )


def kafka_try_send() -> None:
    producer = connect_kafka_producer()
    consumer = KafkaConsumer(
        config.NEW_WINE_MESSAGE_SENT_TOPIC,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
    )

    segm = NewSegmentationIsReadyEvent()

    segm.segmLink = "http://nowhere"
    segm.maskLink = "http://non-existent"
    segm.wineId = "1"

    # serialized = segm.SerializeToString()

    log.info("Sent event: %s", segm)

    publish_message(producer, config.NEW_SEGMENTATION_IS_READY_TOPIC, segm)  # 'msg', str(serialized))
    get_message(consumer)


def serve() -> None:
    producer = connect_kafka_producer()
    consumer = KafkaConsumer(
        config.NEW_WINE_MESSAGE_SENT_TOPIC,
        bootstrap_servers=['localhost:9092'],
        auto_offset_reset='earliest',
    )
    while True:
        process_messages(consumer, producer)
        time.sleep(config.KAFKA_POLLING_TIMEOUT)


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