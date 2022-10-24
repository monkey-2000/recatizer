import json

from kafka import KafkaProducer

class Producer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
            self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                                    value_serializer=lambda v: json.dumps(v).encode('ascii'),
                                    key_serializer=lambda v: json.dumps(v).encode('ascii'))

    def send(self, value, key, topic):
        self.producer.send(topic,
                            key={'id': key},
                            value=value
             )
        self.producer.flush()
        return True