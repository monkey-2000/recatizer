
import os
import time
import logging

from kafka import KafkaConsumer
import multiprocessing.pool as mp_pool
import json

from kafka.consumer.fetcher import ConsumerRecord

from inference.cats_service import CatsService
from inference.configs.db_config import default_db_config
from inference.entities.cat import Cat
from inference.entities.person import Person

logger = logging.getLogger('chat_bot_logger')
_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"



class LimitedMultiprocessingPool(mp_pool.Pool):
    def get_pool_cache_size(self):
        return len(self._cache)


class MsgConsumer:
    FIND_CAT_TOPIC = 'find_cat'
    SAW_CAT_TOPIC = 'saw_cat'
    def __init__(self):
        self.topics = [self.FIND_CAT_TOPIC, self.SAW_CAT_TOPIC]

        self.consumer = KafkaConsumer(
            auto_offset_reset="earliest",
            bootstrap_servers=['localhost:9092'],
            consumer_timeout_ms=1000,
            value_deserializer=lambda v: json.loads(v.decode('ascii')),
            key_deserializer=lambda v: json.loads(v.decode('ascii')),
        )
        self.consumer.subscribe(self.topics)
        self.pool_cache_limit = 1
        self.stop_processing = False
        self.pool = LimitedMultiprocessingPool(processes=2)
        self.inference = CatsService(default_db_config)

    def set_stop_processing(self, *args, **kwargs):
        self.stop_processing = True

    def execute(self, msg: ConsumerRecord):
        topic = msg.topic
        message = msg.value
        if topic == self.FIND_CAT_TOPIC:
            self.inference.add_user(Person(_id=None, path=message['image_path'], quadkey=message["quadkey"],
                   embeddings=None, chat_id=message["user_id"]))
        elif topic == self.SAW_CAT_TOPIC:
            self.inference.save_new_cat(Cat(_id=None, path=message['image_path'], quadkey=message["quadkey"],
                                           embeddings=None, additional_info=message["additional_info"]))

    def main_loop(self):
        while not self.stop_processing:
            for msg in self.consumer:
                logger.info(msg)
                logger.info('%d: %d: k=%s v=%s' % (msg.partition,
                                             msg.offset,
                                             msg.key,
                                             msg.value))
                if self.stop_processing:
                    break
                self.execute(msg)
        self.consumer.close()


if __name__ == '__main__':

    logger.setLevel('INFO')
    fh = logging.FileHandler('consumer.log', 'w', 'utf-8')
    fh.setFormatter(logging.Formatter(_log_format))
    fh.setLevel(level=logging.INFO)

    logger.addHandler(fh)
    logger.setLevel(level=logging.INFO)
    logger.warning("Consumer start.")

    consumer = MsgConsumer()
    consumer.main_loop()




