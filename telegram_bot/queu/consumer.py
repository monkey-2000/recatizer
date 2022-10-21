import os
from datetime import time

from kafka import KafkaConsumer
import json

# To consume latest messages and auto-commit offsets
if __name__ == '__main__':
    consumer = KafkaConsumer('my-topic',
                             client_id='client1',
                             group_id='my-group',
                             bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda v: json.loads(v.decode('ascii')),
                             key_deserializer=lambda v: json.loads(v.decode('ascii')),
                             max_poll_records=10)

    consumer.topics()
    consumer.subscribe(topics='find_cat')
    consumer.subscription()

    for msg in consumer:
        dir(msg)
        print('%d: %d: k=%s v=%s' % (msg.partition,
                                    msg.offset,
                                    msg.key,
                                    msg.value))
        print(msg.topic)
        time.sleep(5*60)
        if os.path.exists(msg.value['answer_dir']):
            matched_path = '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'
            with open(matched_path, "rb") as f:
                photo = f.read()


            with open(msg.value['answer_dir'] + '2022-10-04 23.34.11.jpg', "wb") as f:
                f.write(photo)

     #   photo.download(msg.value.answer_dir + '2022-10-04 23.34.11.jpg')
     #   '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'