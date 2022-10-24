
import os
import time
import logging

from kafka import KafkaConsumer
import multiprocessing.pool as mp_pool
import json

from kafka.errors import kafka_errors

from telegram_bot.configs.bot_cfgs import consumer_msg_cfd

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
                print('msg')
                inference(msg)

## не получилось нормально импортировать кофигурашки при работе из терминала
# class MsgConsumer:
#     ## part of consumer from [https://habr.com/ru/post/587592/]
#     def __init__(self, config, proc_fun=inference):
#         # Функция для обработки сообщения в дочернем процессе
#         self.proc_fun = proc_fun
#         # Клиент для чтения сообщений из Kafka
#         # Клиент для чтения сообщений из Kafka
#         self.consumer = KafkaConsumer(
#             config.kafka_topic,
#             auto_offset_reset=config.auto_offset_reset,
#             enable_auto_commit=config.enable_auto_commit,
#             bootstrap_servers=config.bootstrap_servers,
#             group_id=config.group_id,
#             client_id=config.client_id,
#             check_crcs=config.check_crcs,  # defult value True
#             #consumer_timeout_ms=[float('inf')],  # defult value [float('inf')]
#             session_timeout_ms=config.session_timeout_ms,  # defult value 1000 ms
#             request_timeout_ms=config.request_timeout_ms,  # defult value  305000 ms
#             max_poll_interval_ms=config.max_poll_interval_ms,# defult value  300000 ms
#             max_partition_fetch_bytes=config.max_partition_fetch_bytes,  # defult value  1048576 bytes
#             max_poll_records=config.max_poll_records,  # defult value 500
#             value_deserializer=lambda v: json.loads(v.decode('ascii')),
#             key_deserializer=lambda v: json.loads(v.decode('ascii'))
#         )
#         # Лимит на количество сообщений, единовременно находящихся в пуле
#         self.pool_cache_limit = config.pool_cache_limit
#         # Флаг управляемой остановки приложения
#         self.stop_processing = config.stop_processing
#         # # Пул обработчиков сообщений
#         self.pool = LimitedMultiprocessingPool(processes=config.processes)
#
#     def set_stop_processing(self, *args, **kwargs):
#         self.stop_processing = True
#
#     def handle_pool_cache_excess(self):
#         while self.pool.get_pool_cache_size() >= self.pool_cache_limit:
#             # Здесь можно предусмотреть sleep
#             pass
#
#     def main_loop(self, topics=['find_cat', 'saw_cat']):
#
#         self.consumer.subscribe(topics=topics)
#
#         while not self.stop_processing:
#             for msg in self.consumer:
#                 logger.info('in event loop')
#                 if self.stop_processing:
#                     break
#                 try:
#                     self.handle_pool_cache_excess()
#                     self.consumer.commit()
#                 except kafka_errors.CommitFailedError:
#                     # Отлавливаем редкий, но возможный случай исключения
#                     # при ребалансе
#                     continue
#                 print('2')
#                 self.pool.apply_async(self.proc_fun, (msg,))
#
#     def simple_loop(self, topics=['find_cat', 'saw_cat']):
#             self.consumer.subscribe(topics=topics)
#
#             for msg in self.consumer:
#                 inference(msg)



if __name__ == '__main__':

    logger.setLevel('INFO')
    fh = logging.FileHandler('consumer.log', 'w', 'utf-8')
    fh.setFormatter(logging.Formatter(_log_format))
    fh.setLevel(level=logging.INFO)

    logger.addHandler(fh)
    logger.setLevel(level=logging.INFO)
    logger.warning("Consumer start.")

    consumer = MsgConsumer(proc_fun=inference)
    # consumer = MsgConsumer(config=consumer_msg_cfd, proc_fun=inference)
    # consumer.main_loop() # Need to debug this loop!!! There is an error AttributeError: 'dict' object has no attribute 'CommitFailedError'
    consumer.simple_loop()




