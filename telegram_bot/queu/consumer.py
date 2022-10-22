
import os
import time
import logging

from kafka import KafkaConsumer
import multiprocessing.pool as mp_pool
import json

from kafka.errors import kafka_errors

logger = logging.getLogger('chat_bot_logger')
_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"



class LimitedMultiprocessingPool(mp_pool.Pool):
    def get_pool_cache_size(self):
        return len(self._cache)

def inference(msg):
    print('inference')
    logger.info(f'partition {msg.partition}, msg.offset {msg.offset} \\n msg.key  {msg.key} msg.value {msg.value}')
    # consumer.commit()

    # msg = next(consumer)
    # consumer.commit({TopicPartition("topic_name", msg.partition): OffsetAndMetadata(msg.offset + 1, '')})
    print('%d: %d: k=%s v=%s' % (msg.partition,
                                 msg.offset,
                                 msg.key,
                                 msg.value))
    print(msg.topic)
    time.sleep(60)
    if os.path.exists(msg.value['answer_dir']):
        matched_path = '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'
        with open(matched_path, "rb") as f:
            photo = f.read()

        with open(msg.value['answer_dir'] + '2022-10-04 23.34.11.jpg', "wb") as f:
            f.write(photo)

class MsgConsumer:
    ## part of consumer from [https://habr.com/ru/post/587592/]
    def __init__(self, proc_fun=inference):
        # Функция для обработки сообщения в дочернем процессе
        self.proc_fun = proc_fun
        # Клиент для чтения сообщений из Kafka
        # Клиент для чтения сообщений из Kafka
        self.consumer = KafkaConsumer(
            'my-topic',
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            bootstrap_servers=['localhost:9092'],
            group_id='my-group',
            client_id='client1',
            check_crcs=True,  # defult value True
            #consumer_timeout_ms=[float('inf')],  # defult value [float('inf')]
            session_timeout_ms=10000,  # defult value 1000 ms
            request_timeout_ms=305000,  # defult value  305000 ms
            max_poll_interval_ms=300000*10,# defult value  300000 ms
            max_partition_fetch_bytes=1048576,  # defult value  1048576 bytes
            max_poll_records=1000,  # defult value 500
            value_deserializer=lambda v: json.loads(v.decode('ascii')),
            key_deserializer=lambda v: json.loads(v.decode('ascii')),
        )
        # Лимит на количество сообщений, единовременно находящихся в пуле
        self.pool_cache_limit = 1
        # Флаг управляемой остановки приложения
        self.stop_processing = False
        # # Пул обработчиков сообщений
        self.pool = LimitedMultiprocessingPool(processes=2)

    def set_stop_processing(self, *args, **kwargs):
        self.stop_processing = True

    def handle_pool_cache_excess(self):
        while self.pool.get_pool_cache_size() >= self.pool_cache_limit:
            # Здесь можно предусмотреть sleep
            pass

    def main_loop(self, topics=['find_cat', 'saw_cat']):

        self.consumer.subscribe(topics=topics)

        while not self.stop_processing:
            for msg in self.consumer:
                logger.info('in event loop')
                if self.stop_processing:
                    break
                try:
                    self.handle_pool_cache_excess()
                    self.consumer.commit()
                except kafka_errors.CommitFailedError:
                    # Отлавливаем редкий, но возможный случай исключения
                    # при ребалансе
                    continue
                print('2')
                self.pool.apply_async(self.proc_fun, (msg,))

    def simple_loop(self, topics=['find_cat', 'saw_cat']):
            self.consumer.subscribe(topics=topics)

            for msg in self.consumer:
                inference(msg)


# To consume latest messages and auto-commit offsets
if __name__ == '__main__':

    logger.setLevel('INFO')
    fh = logging.FileHandler('consumer.log', 'w', 'utf-8')
    fh.setFormatter(logging.Formatter(_log_format))
    fh.setLevel(level=logging.INFO)

    logger.addHandler(fh)
    logger.setLevel(level=logging.INFO)
    logger.warning("Consumer start.")

    consumer = MsgConsumer()
    # consumer.main_loop()
    consumer.simple_loop()

    # consumer = KafkaConsumer('my-topic',
    #                          client_id='client1',
    #                          group_id='my-group',
    #                          bootstrap_servers=['localhost:9092'],
    #                          value_deserializer=lambda v: json.loads(v.decode('ascii')),
    #                          key_deserializer=lambda v: json.loads(v.decode('ascii')),
    #                          max_poll_records=1000)
    # #                         request_timeout_ms=305000 * 100)

    # Traceback(most
    # recent
    # call
    # last):
    # File
    # "/home/art/PycharmProjects/recatizer/telegram_bot/queu/consumer.py", line
    # 23, in < module >
    # consumer = KafkaConsumer('my-topic',
    #                          File
    # "/home/art/anaconda3/lib/python3.9/site-packages/kafka/consumer/group.py", line
    # 332, in __init__
    # raise KafkaConfigurationError(
    #     kafka.errors.KafkaConfigurationError: KafkaConfigurationError: connections_max_idle_ms(540000)
    # must
    # be
    # larger
    # than
    # request_timeout_ms(30500000)
    # which
    # must
    # be
    # larger
    # than
    # fetch_max_wait_ms(500).

    # kafka.errors.CommitFailedError: CommitFailedError: Commit
    # cannot
    # be
    # completed
    # since
    # the
    # group
    # has
    # already
    # rebalanced and assigned
    # the
    # partitions
    # to
    # another
    # member.
    # This
    # means
    # that
    # the
    # time
    # between
    # subsequent
    # calls
    # to
    # poll()
    # was
    # longer
    # than
    # the
    # configured
    # max_poll_interval_ms, which
    # typically
    # implies
    # that
    # the
    # poll
    # loop is spending
    # too
    # much
    # time
    # message
    # processing.You
    # can
    # address
    # this
    # either
    # by
    # increasing
    # the
    # rebalance
    # timeout
    # with max_poll_interval_ms,
    #     or by
    #     reducing
    #     the
    #     maximum
    #     size
    #     of
    #     batches
    #     returned in poll()
    # with max_poll_records.

    # consumer.topics()
    # consumer.subscribe(topics='find_cat')
    # consumer.subscription()

    # for msg in consumer:
    #     dir(msg)
    #     logger.info(f'partition {msg.partition}, msg.offset {msg.offset} \\n msg.key  {msg.key} msg.value {msg.value}')
    #     #consumer.commit()
    #
    #     # msg = next(consumer)
    #     # consumer.commit({TopicPartition("topic_name", msg.partition): OffsetAndMetadata(msg.offset + 1, '')})
    #     print('%d: %d: k=%s v=%s' % (msg.partition,
    #                                 msg.offset,
    #                                 msg.key,
    #                                 msg.value))
    #     print(msg.topic)
    #     time.sleep(45)
    #     if os.path.exists(msg.value['answer_dir']):
    #         matched_path = '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'
    #         with open(matched_path, "rb") as f:
    #             photo = f.read()
    #
    #
    #         with open(msg.value['answer_dir'] + '2022-10-04 23.34.11.jpg', "wb") as f:
    #             f.write(photo)

     #   photo.download(msg.value.answer_dir + '2022-10-04 23.34.11.jpg')
     #   '/home/art/PycharmProjects/recatizer/app/images/2022-10-04 23.34.11.jpg'