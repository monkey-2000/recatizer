import json

from kafka import KafkaProducer


from telegram_bot.configs.bot_cfgs import bot_config


class Producer:
    def __init__(self, bootstrap_servers=bot_config.kafka_server):
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