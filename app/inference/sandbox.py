import json

from kafka import KafkaConsumer

#from app.inference.queue.queue_tool import QUEUE_CONFIG


from app.inference.queue.queue_tool import Producer, Consumer


def mathing_cat(cat_img_path):
    '''find cat in our database'''
    ##model.predict(cat_img_path)
    return cat_img_path


if __name__ == '__main__':
    consumer = Consumer()
    consumer.consumer.subscribe(topics='find_cat')
    # producer = Producer(topic='No')
    for msg in consumer.consumer:
            print('%d: %d: k=%s v=%s' % (msg.partition,
                                         msg.offset,
                                         msg.key,
                                         msg.value))
            matched_cat = mathing_cat(msg.value['path'])
            # producer.topic = str(msg.value['chat_id'])
            # producer.send({'matched_cat': matched_cat})
            # print(msg.topic)


