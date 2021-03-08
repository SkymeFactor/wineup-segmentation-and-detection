from __future__ import unicode_literals

import segmentation_pb2 as msg
from kafka import KafkaConsumer, KafkaProducer

topic = 'unknown_topic'

log = []

def connect_kafka_producer():
    _producer = None
    try:
        _producer = KafkaProducer(bootstrap_servers=['kafka:9092'])
    except Exception:
        log.append('producer connection failed')
        pass
    finally:
        log.append('producer connection success')
        return _producer


def publish_message(producer_instance, topic_name, data):
    try:
        #key_bytes = bytes(str(key), encoding='utf-8')
        #value_bytes = bytes(str(value), encoding='utf-8')
        #print(data)
        producer_instance.send(topic_name, data.SerializeToString())#key=key_bytes, value=value_bytes)
        producer_instance.flush()
        log.append('Message successfully sent')
    except Exception as e:
        log.append(str(e))


def get_message(consumer):
    links = []
    for message in consumer:
        value = message.value
        link = msg.Segmentation()
        link.ParseFromString(value)
        log.append('Message successfully received')
        #log.append(str(link))
        links.append(link)
        return links

def kafka_try_send():
    producer = connect_kafka_producer()
    consumer = KafkaConsumer(topic, bootstrap_servers=['kafka:9092'], auto_offset_reset='earliest')

    segm = msg.Segmentation()

    segm.segm_link = "http://nowhere"
    segm.mask_link = "http://non-existent"
    segm.id = 1

    #serialized = segm.SerializeToString()

    log.append(str(segm))

    publish_message(producer, topic, segm)#'msg', str(serialized))
    links = get_message(consumer)

    log.append(str(links[0]))

    d = {}
    for i in range(len(log)):
        d.update({'line ' + str(i): log[i]})

    return d

#print(json.dumps(kafka_try_send()))

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