import logging
import sys
from time import time

from kafka import KafkaConsumer
import multiprocessing.pool as mp_pool
import json
from kafka.consumer.fetcher import ConsumerRecord

from src.services.cats_service import CatsService
from src.configs.service_config import default_service_config
from src.entities.cat import Cat
from src.entities.person import Person

logger = logging.getLogger('chat_bot_logger')
_log_format = f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"



class LimitedMultiprocessingPool(mp_pool.Pool):
    def get_pool_cache_size(self):
        return len(self._cache)


class MsgConsumer:
    FIND_CAT_TOPIC = 'find_cat'
    SAW_CAT_TOPIC = 'saw_cat'
    NEW_SEARCH = "new_search"
    MARK_ANSWER ="mark_user_answer"
    MATCH_EXTRA="get_match_extra"
    def __init__(self):
        self.topics = [self.FIND_CAT_TOPIC,
                       self.SAW_CAT_TOPIC,
                       self.NEW_SEARCH,
                       self.MARK_ANSWER,
                       self.MATCH_EXTRA]

        self.consumer = KafkaConsumer(
            auto_offset_reset="latest",
            bootstrap_servers=['localhost:9092'],
            consumer_timeout_ms=1000,
            value_deserializer=lambda v: json.loads(v.decode('ascii')),
            key_deserializer=lambda v: json.loads(v.decode('ascii')),
        )
        self.consumer.subscribe(self.topics)
        self.pool_cache_limit = 1
        self.stop_processing = False
        self.pool = LimitedMultiprocessingPool(processes=2)
        self.inference = CatsService(default_service_config)

    def set_stop_processing(self, *args, **kwargs):
        self.stop_processing = True

    def execute(self, msg: ConsumerRecord):
        topic = msg.topic
        message = msg.value
        if topic == self.FIND_CAT_TOPIC:
            self.inference.add_user(
                Person(
                    _id=None,
                    paths=message["image_paths"],
                    quadkey=message["quadkey"],
                    embeddings=None,
                    is_active=True,
                    additional_info=message["additional_info"],
                    chat_id=message["user_id"],
                    dt=-float("inf"),
                )
            )
        elif topic == self.SAW_CAT_TOPIC:
            # TODO case with two cats!!!!!
            self.inference.save_new_cat(
                Cat(
                    _id=None,
                    paths=message["image_paths"],
                    quadkey=message["quadkey"],
                    embeddings=None,
                    is_active=True,
                    additional_info=message["additional_info"],
                    chat_id=message["user_id"],
                    person_name=message["person_name"],
                    dt=time(),
                )
            )

        elif topic == self.NEW_SEARCH:
            print("New SEARCH")
            wanted_cat = self.inference.people_db.find({'chat_id': message["user_id"], "is_active": True})
            self.inference.find_similar_cats(wanted_cat)

        elif topic == self.MARK_ANSWER:
            self.inference.mark_user_answer(message)

        elif topic == self.MATCH_EXTRA:
            print('extra')
            # kafka_message = {"cat_ids": cat_id,
            #                  "chat_id": chat_id},
            pass


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
                # self.consumer.commit()

        self.consumer.close()


if __name__ == '__main__':

    logger.setLevel('INFO')
    fh = logging.StreamHandler(sys.stdout)
    fh.setFormatter(logging.Formatter(_log_format))
    fh.setLevel(level=logging.INFO)

    logger.addHandler(fh)
    logger.setLevel(level=logging.INFO)
    logger.warning("Consumer start.")

    consumer = MsgConsumer()
    consumer.main_loop()




