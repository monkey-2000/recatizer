from kafka import KafkaProducer


class Producer:
    def __init__(self, bootstrap_servers=['localhost:9092']):
            self.producer = KafkaProducer(bootstrap_servers=['localhost:9092'],
                                    value_serializer=lambda v: json.dumps(v).encode('ascii'),
                                    key_serializer=lambda v: json.dumps(v).encode('ascii'))

    def send(self, value, key):
        self.producer.send('find_cat',
              key={'id': key},
              value=value
             )
        self.producer.flush()
        return True