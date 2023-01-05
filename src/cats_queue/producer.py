import json

from kafka import KafkaProducer

from src.configs.service_config import default_service_config as config


class Producer:
    def __init__(self, bootstrap_servers=config.kafka_broker_ip):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("ascii"),
            key_serializer=lambda v: json.dumps(v).encode("ascii"),
        )

    def send(self, value, key, topic):
        self.producer.send(topic, key={"id": key}, value=value)
        self.producer.flush()
        return True
